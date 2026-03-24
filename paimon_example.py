import pypaimon
import pypaimon.common.file_io as _fio
from pyarrow.fs import S3FileSystem

# pypaimon이 force_virtual_addressing=True를 하드코딩하고 있어
# MinIO path-style 접근 불가 → S3FileSystem 직접 주입
_orig_init = _fio.FileIO.__init__


def _patched_init(self: _fio.FileIO, path: str, catalog_options: dict) -> None:
    _orig_init(self, path, catalog_options)
    scheme, _, _ = self.parse_location(path)
    if scheme in ("s3", "s3a", "s3n"):
        self.filesystem = S3FileSystem(
            endpoint_override=catalog_options.get("fs.s3.endpoint"),
            access_key=catalog_options.get("fs.s3.accessKeyId"),
            secret_key=catalog_options.get("fs.s3.accessKeySecret"),
            allow_bucket_creation=False,
            force_virtual_addressing=False,
        )


_fio.FileIO.__init__ = _patched_init  # type: ignore[assignment]

catalog = pypaimon.CatalogFactory.create({
    "type": "filesystem",
    "warehouse": "s3://warehouse/paimon",
    "fs.s3.endpoint": "http://localhost:9000",
    "fs.s3.accessKeyId": "admin",
    "fs.s3.accessKeySecret": "password123",
})

table = catalog.get_table("wikidb.wiki_changes")
read_builder = table.new_read_builder()
scan = read_builder.new_scan()
splits = scan.plan().splits()
reader = read_builder.new_read()

# pypaimon 내장 to_duckdb: splits → Arrow → DuckDB 자동 처리
con = reader.to_duckdb(splits, "wiki_data")

result = con.execute("""
    SELECT wiki, COUNT(*) as edits,
           SUM(CASE WHEN bot THEN 1 ELSE 0 END) as bot_edits
    FROM wiki_data
    GROUP BY wiki
    ORDER BY edits DESC
    LIMIT 20
""").fetchdf()
result = con.sql("SELECT count(*), count(distinct id) FROM wiki_data").fetchdf()
print(result)
