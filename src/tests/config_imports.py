import sys
import os

root_path = os.path.abspath(".")
sys.path.append(f"{root_path}/src/service/company/")
sys.path.append(f"{root_path}/src/service/user_details/")
sys.path.append(f"{root_path}/src/service/company_report_vs_peers")
sys.path.append(f"{root_path}/src/service/comparison_vs_peers")
sys.path.append(f"{root_path}/src/service/universe_overview")
sys.path.append(f"{root_path}/src/service/user_details")
sys.path.append(f"{root_path}/src/service/users")
sys.path.append(f"{root_path}/casbin_configuration/")
sys.path.append(f"{root_path}/db/utils/")
sys.path.append(f"{root_path}/src/utils/")
sys.path.append(f"{root_path}/src/handlers")
sys.path.append(f"{root_path}/src/handlers/comparison_vs_peers")
