from pipeline.factory import PipelineFactory


def main():
    operation_type = "local_operation"  # or "update_description"
    mode = "local"  # or "aws"

    factory = PipelineFactory(mode=mode)
    pipeline = factory.create_pipeline(operation_type)

    entity_list = {"db1": ["table1", "table2"], "db2": ["table1"]}

    results = pipeline.run(entity_list)

    print("\nDataset Processed:")
    print(results["evaluated"])
    print("\nGlobal Summary:")
    print(results["summary"])


if __name__ == "__main__":
    main()
