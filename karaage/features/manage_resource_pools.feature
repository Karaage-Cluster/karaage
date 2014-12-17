Feature: Manage resource pools
	As an administrator
	I want to manage machine resources in groups (resource pools)
	So that allocations can be made across all grouped resources rather than individual machine resources

	Background: Logged in as admin with test data available
		Given test data is loaded
		And I am logged in as an administrator

	Scenario: View resource pools
		Given I am on the resource pools page
		Then I should see a resource pool named "Compute SU"
		Then I should see a "Compute SU" resource pool with scaled quantity of "52,428.8"

	Scenario: Add new resource pool
		Given I am on the resource pools page
		When I add a resource pool named "Mega SU"
		Then there are resources in the pool
		Then I should see a "Mega SU" resource pool with scaled quantity of "0.0"

	Scenario: Add resource to resource pool
		Given I am on the resource pools page
		And I edit the "Compute SU" resource pool
		And there are resources in the pool
			| machine | type | quantity | scaling_factor |
			| avoca   | CPU  | 65536    | 0.8            |
		When I add resources to the pool
			| machine | type | quantity | scaling_factor |
			| barcoo  | CPU  | 1120     | 4.0            |
		And I save
		Then I should see a "Compute SU" resource pool with scaled quantity of "56,908.8"
