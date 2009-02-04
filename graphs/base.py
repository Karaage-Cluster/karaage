"""
Module for abstract graph generation base classes.
"""


class GraphGenerator(object):

    def gen_project_graph(self, project, start, end, machine_category):
        """Generates a bar graph for a project
    
        Keyword arguments:
        project -- Project
        start -- start date
        end -- end date
        machine_category -- MachineCategory object
    
        """
        raise NotImplementedError

    def gen_institutes_pie(self, start, end, machine_category):
        """Generates a pie graph showing all primary institutes usage
    
        Keyword arguments:
        start -- start date
        end -- end date
        machine_category -- MachineCategory object
        
        """
        raise NotImplementedError


    def gen_quota_graph(self):
        """Generates a pie graph for all primary institutes quota       
        """
        raise NotImplementedError



    def gen_trend_graph(self, start, end, machine_category):
        """Generates a bar graph showing the trend usage for a machine category
        
        Keyword arguments:
        start -- start date
        end -- end date
        machine_category -- MachineCategory object
        """
        pass
        #raise NotImplementedError
    
    
    def gen_institute_bar(self, institute, start, end, machine_category): 
        """Generates a bar graph showing the trend usage for an institute

        Keyword arguments:
        institute -- Institute
        start -- start date
        end -- end date
        machine_category -- MachineCategory object
        """
        pass
        #raise NotImplementedError

