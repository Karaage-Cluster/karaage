# Copyright 2007-2010 VPAC
#
# This file is part of Karaage.
#
# Karaage is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Karaage is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Karaage  If not, see <http://www.gnu.org/licenses/>.

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
        pass

    def gen_institutes_pie(self, start, end, machine_category):
        """Generates a pie graph showing all active institutes usage
    
        Keyword arguments:
        start -- start date
        end -- end date
        machine_category -- MachineCategory object
        
        """
        pass


    def gen_quota_graph(self):
        """Generates a pie graph for all active institutes quota       
        """
        pass



    def gen_trend_graph(self, start, end, machine_category):
        """Generates a bar graph showing the trend usage for a machine category
        
        Keyword arguments:
        start -- start date
        end -- end date
        machine_category -- MachineCategory object
        """
        
        pass
    
    
    def gen_institute_bar(self, institute, start, end, machine_category): 
        """Generates a bar graph showing the trend usage for an institute

        Keyword arguments:
        institute -- Institute
        start -- start date
        end -- end date
        machine_category -- MachineCategory object
        """

        pass

