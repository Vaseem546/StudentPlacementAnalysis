import sys
from dotenv import load_dotenv

load_dotenv()

from dbt.cli.main import dbtRunner

if __name__ == "__main__":
    args = sys.argv[1:] if len(sys.argv) > 1 else ["run"]
    cli_args = args + ["--project-dir", "dbt_project", "--profiles-dir", "dbt_project"]
    print(f"Executing: dbt {' '.join(cli_args)}")
    res = dbtRunner().invoke(cli_args)
    if not res.success:
        print("dbt execution finished with errors.")
        sys.exit(1)
    print("dbt execution completed successfully.")
