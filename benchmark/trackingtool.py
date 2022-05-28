import pandas as pd
from datetime import datetime
import uuid
import os
import schedule


class Tracker:
    def __init__(self, save_dir='.'):
        self.criteria_list = ['time'] # date and time are always tracked
        self.data_frame = pd.DataFrame(columns=self.criteria_list)
        self.save_dir = save_dir
        if not os.path.exists(self.save_dir):
            os.mkdir(self.save_dir)
    
    def add_criteria(self, criteria_list):
        """Add a new list of tracking criteria to the tracking system

        Args:
            criteria_list (list): List of criteria (str)

        Raises:
            ValueError: Can't add new criteria when the TrackingTool already have data
        """
        if len(self.data_frame) != 0:
            raise ValueError("Can't add criteria because there are data in tracked!")
        
        else:
            self.criteria_list.extend(criteria_list)
            self.data_frame = pd.DataFrame(columns=self.criteria_list)
            
    def track(self, report_dict):
        """Track system info

        Args:
            report_dict (dict): New system info
        """
        
        # Add time info
        now = datetime.now()
        report_dict['time'] = now.strftime("%d/%m/%Y %H:%M:%S")

        # Check data compatibility
        keys = report_dict.keys()
        assert sorted(keys) == sorted(self.criteria_list), "The key list is not compatible with the tracking data"
        
        # New data
        index = len(self.data_frame)
        report = pd.DataFrame(report_dict, index=[index])
        
        # Concat to dataframe
        self.data_frame = pd.concat([self.data_frame, report])
        
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
            schedule.every(every).seconds.do(self.save_and_reset)
        
        elif period == 'minute':
            schedule.every(every).minutes.do(self.save_and_reset)
        
        elif period == 'hour':
            schedule.every(every).hour.do(self.save_and_reset)
            
        elif period == 'day':
            schedule.every(every).day.do(self.save_and_reset)
    
    def run_pending(self):
        """Check for pending task
        """
        schedule.run_pending()
    
    
    def save_and_reset(self):
        """Save and reset
        """
        
        # Create unique filename
        now = datetime.now()
        today = datetime.today()
        filename = "{}-{}-{}.csv".format(
            today.strftime('%Y-%m-%d'),
            now.strftime('%H-%M-%S'),
            uuid.uuid1()
        )
        
        # Save
        self.data_frame.to_csv(os.path.join(self.save_dir, filename), index=False)
        
        # Reset data
        self.data_frame.drop(self.data_frame.index, inplace=True)
        
    def load_all_data(self):
        """Load all saved csv file

        Returns:
            df (DataFrame): All tracked info
        """
        filelist = os.listdir(self.save_dir)
        filelist.sort()
        assert len(filelist) > 0, "No data found"
        
        csv_list = []
        
        for file in filelist:
            link = os.path.join(self.save_dir, file)
            print('Reading {} ...'.format(file))
            tmp = pd.read_csv(link)
            
            # Add file with same criteria
            if tmp.keys() == self.criteria_list:
                csv_list.append(tmp)
            
        df = pd.concat(csv_list)
        df.reset_index(inplace=True)
        return df
    
    def load_latest_data(self):
        """Load the latest data saved
        """
        
        filelist = os.listdir(self.save_dir)
        filelist.sort()
        assert len(filelist) > 0, "No data found"
        
        file = filelist[-1]
        link = os.path.join(self.save_dir, file)
        df = pd.read_csv(link)
        df.reset_index(inplace=True)
        return df
    
    def has_saved(self):
        """Check if there any file saved

        Returns:
            result (bool)
        """
        return len(os.listdir(self.save_dir)) > 0
        
        
        
        
        
            
            
        
        
        
        
        
        
        
    
        
        
        