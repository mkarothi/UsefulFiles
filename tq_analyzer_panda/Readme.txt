

# TeamQuest Analyzer Read Me Document  

		- This analyzer package was mainly developed to analyze the criticality of the system in automated way
		- This program solves multiple server analyzers within max of 5 minutes
	
What will analyze this Teamquest analyzer?
	
		This package will analyze all the below listed metrics, and further more, it will be going to extend based on the needs
		
			- CPU Criticality based on the CPU utilization and CPU Queue 
			- Memory Criticality based on the percentage of Memory used
			- Disk Criticality based on the percentage of disk utilized and Disk queue
			- Disk Latency based on the disk response time
			- Swap Criticality based on the swap utilization

How Can I Define or Change the critical/warning configuration for the metrics?
	
	You need to define what's critical or warning for each metrics in the config.ini file placed inside "Teamquest_Analyzer_v2.0.1" folder
	
How can I include new metrics analysis in the TeamQuest Analyzer?

	You need to include the module inside the "Teamquest_Analyzer_v2.0.1\lib"  directory
	which holds  each metrics analyzer as module and the main.py  which calls all this module and do the entire analyzer operations
	