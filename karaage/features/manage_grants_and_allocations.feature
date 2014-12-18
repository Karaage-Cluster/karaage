Feature:
	As an administrator
	I want to manage project resource allocations in groups (allocation pools)
	So that usage can be recorded against project specific allocation pools

	Background: Logged in as admin with test data available
		Given test data is loaded
		And the time is now "2015-01-01 00:01"
		And I am logged in as an administrator

	Scenario: View and add project allocations
		Given I am on the "Karaage 4" project page
		And I can see allocation pools
			| resource_pool | period  | quantity | used | remaining | percent |
			| Compute SU    | 2015 Q1 |   10,000 |    0 |    10,000 |    0.0% |
			| GPFS Disk GB  | 2015 Q1 |    2,000 |    0 |     2,000 |    0.0% |
			| Compute SU    | 2015 Q2 |   10,000 |    0 |    10,000 |    0.0% |
			| GPFS Disk GB  | 2015 Q2 |    2,000 |    0 |     2,000 |    0.0% |
			| Compute SU    | 2015 Q3 |   10,000 |    0 |    10,000 |    0.0% |
			| GPFS Disk GB  | 2015 Q3 |    2,000 |    0 |     2,000 |    0.0% |
			| Compute SU    | 2015 Q4 |   10,000 |    0 |    10,000 |    0.0% |
			| GPFS Disk GB  | 2015 Q4 |    2,000 |    0 |     2,000 |    0.0% |
		And I can see allocations
			| resource_pool | period  | grant   | quantity |
			| Compute SU    | 2015 Q1 | Initial | 10000    |
			| GPFS Disk GB  | 2015 Q1 | Initial | 2000     |
			| Compute SU    | 2015 Q2 | Initial | 10000    |
			| GPFS Disk GB  | 2015 Q2 | Initial | 2000     |
			| Compute SU    | 2015 Q3 | Initial | 10000    |
			| GPFS Disk GB  | 2015 Q3 | Initial | 2000     |
			| Compute SU    | 2015 Q4 | Initial | 10000    |
			| GPFS Disk GB  | 2015 Q4 | Initial | 2000     |
		When I add allocations
			| resource_pool | period  | grant   | quantity |
			| Compute SU    | 2015 Q1 | Bonus   | 5000     |
			| GPFS Disk GB  | 2015 Q1 | Bonus   | 500      |
		Then I can see allocation pools
			| resource_pool | period  | quantity | used | remaining | percent |
			| Compute SU    | 2015 Q1 |   15,000 |    0 |    15,000 |    0.0% |
			| GPFS Disk GB  | 2015 Q1 |    2,500 |    0 |     2,500 |    0.0% |
			| Compute SU    | 2015 Q2 |   10,000 |    0 |    10,000 |    0.0% |
			| GPFS Disk GB  | 2015 Q2 |    2,000 |    0 |     2,000 |    0.0% |
			| Compute SU    | 2015 Q3 |   10,000 |    0 |    10,000 |    0.0% |
			| GPFS Disk GB  | 2015 Q3 |    2,000 |    0 |     2,000 |    0.0% |
			| Compute SU    | 2015 Q4 |   10,000 |    0 |    10,000 |    0.0% |
			| GPFS Disk GB  | 2015 Q4 |    2,000 |    0 |     2,000 |    0.0% |
		And I can see allocations
			| resource_pool | period  | grant   | quantity |
			| Compute SU    | 2015 Q1 | Initial | 10000    |
			| Compute SU    | 2015 Q1 | Bonus   | 5000     |
			| GPFS Disk GB  | 2015 Q1 | Initial | 2000     |
			| GPFS Disk GB  | 2015 Q1 | Bonus   | 500      |
			| Compute SU    | 2015 Q2 | Initial | 10000    |
			| GPFS Disk GB  | 2015 Q2 | Initial | 2000     |
			| Compute SU    | 2015 Q3 | Initial | 10000    |
			| GPFS Disk GB  | 2015 Q3 | Initial | 2000     |
			| Compute SU    | 2015 Q4 | Initial | 10000    |
			| GPFS Disk GB  | 2015 Q4 | Initial | 2000     |
