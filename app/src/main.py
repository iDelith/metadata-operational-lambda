import json


def main():

    # Setting main objects
    entity_list = {"ics_database_1": ["table1", "table2"], "ics_database_2": ["table1"]}

    # Sanity check
    print("Entity List:\n", json.dumps(entity_list, indent=4))

    # Control variable
    dataset_processed = {}

    # Main iterator
    for db_name, tables in entity_list.items():
        print("\nProcessing database:", db_name)
        dataset_processed[db_name] = {"result": None, "tables": {}}

        for table in tables:
            try:
                # -----------------------------,
                #                              |
                # Glue client logic            |
                #                              |
                # -----------------------------`

                # If processing is successful
                dataset_processed[db_name]["tables"][table] = {
                    "status": "SUCCESS",
                    "error": None,
                }

            except Exception as e:
                # On failure
                dataset_processed[db_name]["tables"][table] = {
                    "status": "FAILURE",
                    "error": str(e),
                }

        # Evaluate overall database result
        for db_name, entries in dataset_processed.items():
            table_status = [table["status"] for table in entries["tables"].values()]

            entries["result"] = (
                "SUCCESS"
                if all(status == "SUCCESS" for status in table_status)
                else "FAILURE"
            )

        # Compute global summary
        global_summary = {
            "databases_total": len(dataset_processed),
            "databases_success": sum(
                1 for db in dataset_processed.values() if db["result"] == "SUCCESS"
            ),
            "databases_failure": sum(
                1 for db in dataset_processed.values() if db["result"] == "FAILURE"
            ),
            "tables_total": sum(len(db["tables"]) for db in dataset_processed.values()),
            "tables_success": sum(
                1
                for db in dataset_processed.values()
                for t in db["tables"].values()
                if t["status"] == "SUCCESS"
            ),
            "tables_failure": sum(
                1
                for db in dataset_processed.values()
                for t in db["tables"].values()
                if t["status"] == "FAILURE"
            ),
        }

    # Summary outcomes
    print("\nDataset Processed:\n", json.dumps(dataset_processed, indent=4))

    print("\nGlobal Summary:\n")
    print(json.dumps(global_summary, indent=4))


if __name__ == "__main__":
    main()
