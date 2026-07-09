"""
Entry point: runs the Olist API source through dlt, landing everything
into the `bronze` schema of the analytics warehouse Postgres instance.

This is intentionally a thin script — all the real logic lives in
sources/olist_api.py. This file just wires source -> destination and
triggers a run.
"""
import dlt

from sources.olist_api import olist_api_source


def main():
    pipeline = dlt.pipeline(
        pipeline_name="olist_elt_pipeline",
        destination="postgres",
        dataset_name="bronze",
    )

    load_info = pipeline.run(olist_api_source())
    print(load_info)


if __name__ == "__main__":
    main()