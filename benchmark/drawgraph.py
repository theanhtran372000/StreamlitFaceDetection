import streamlit as st
import schedule

class GraphDrawer():
    def __init__(self, tracker):
        self.graph_dict = dict()
        self.tracker = tracker
        
    def add_graph(self, title, attribute_list, index='time'):
        """Add graph placeholder with title

        Args:
            title (str): Title of the graph
            attribute_list (list): List of attribute shown on the graph
        """
        assert index in attribute_list, '{} not in {}'.format(index, attribute_list)
        
        st.markdown('**{}**'.format(title.upper()))
        self.graph_dict[title] = dict()
        self.graph_dict[title]['figure'] = st.empty()
        self.graph_dict[title]['attrs'] = attribute_list
        self.graph_dict[title]['index'] = index
    
    def draw(self):
        """Draw or update all graph
        """
        if self.tracker.has_saved():
            # Load latest data
            latest_data = self.tracker.load_latest_data()
            
            # Update graph
            for _, graph in self.graph_dict.items():
                graph['figure'].line_chart(latest_data[graph['attrs']].set_index(graph['index']))
                
        else:
            for _, graph in self.graph_dict.items():
                graph['figure'].write('No data available!')
            
    
    def config_scheduler(self, every=5, period='minute'):
        """Config scheduler for save and reset memory

        Args:
            every (int): Time stamp. Defaults to 5.
            period (str): Time unit. Defaults to 'minute'.
        """
        
        # Check
        support_list = ['second', 'minute', 'hour', 'day']
        assert period in support_list, "Scheduler only supports one of these {}".format(support_list)
        
        # Config scheduler
        if period == 'second':
            schedule.every(every).seconds.do(self.draw)
        
        elif period == 'minute':
            schedule.every(every).minutes.do(self.draw)
        
        elif period == 'hour':
            schedule.every(every).hour.do(self.draw)
            
        elif period == 'day':
            schedule.every(every).day.do(self.save_and_reset)
            
    def run_pending(self):
        """Check the schedule
        """
        schedule.run_pending()
            