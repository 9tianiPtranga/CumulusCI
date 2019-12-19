from cumulusci.tasks.salesforce import BaseSalesforceApiTask
from cumulusci.core.utils import process_list_arg


class ActivateFlowProcesses(BaseSalesforceApiTask):
    """
    Activate the Flows with the supplied Developer Names
    """

    def _init_options(self, kwargs):
        self.options = {}
        self.options["developer_names"] = process_list_arg(
            self.task_config.options["developer_names"]
        )
        print(self.task_config.options)

    api_version = "43.0"

    def _run_task(self):
        self.logger.info(
            f"Activating the following Flows: {self.options['developer_names']}"
        )
        self.logger.info("Querying flow definitions...")
        res = self.tooling.query(
            "SELECT Id, ActiveVersion.VersionNumber, LatestVersion.VersionNumber, DeveloperName FROM FlowDefinition WHERE DeveloperName IN ({0})".format(
                ",".join([f"'{n}'" for n in self.options.get("developer_names")])
            )
        )
        for listed_flow in res["records"]:
            self.logger.info(f'Processing: {listed_flow["DeveloperName"]}')
            path = f"tooling/sobjects/FlowDefinition/{listed_flow['Id']}"
            urlpath = self.sf.base_url + path
            data = {
                "Metadata": {
                    "activeVersionNumber": listed_flow["LatestVersion"]["VersionNumber"]
                }
            }
            response = self.tooling._call_salesforce("PATCH", urlpath, json=data)
            self.logger.info(response)
