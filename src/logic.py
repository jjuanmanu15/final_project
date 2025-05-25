import random
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image
import numpy as np
import io
import os

class Competition:
    """Initializes csv."""
    def __init__(self):
        self.participants = {}
        self.csv_file = "participants_data.csv" 
        self.load_from_csv() 

    def load_from_csv(self):
        """Load participant data from CSV file using pandas"""
        if os.path.exists(self.csv_file):
            try:
                df = pd.read_csv(self.csv_file)
                for _, row in df.iterrows(): #Iterates through the csv ignoring the index, the "_" is for that
                    self.participants[row['Name']] = {
                        'Scores': [float(row['Resistence']), float(row['Strength']), float(row['Velocity'])],
                        'Difficulties': [float(row['Resistence_Difficulty']), float(row['Strength_Difficulty']),
                                        float(row['Velocity_Difficulty'])],
                        'Final punctuation': float(row['Final_Punctuation']),
                        'Qualified?': row['Qualified'] == 'Yes'
                    }
            except Exception as e:
                print(f"Couldn't load CSV data - {str(e)}")

    def save_to_csv(self):
        """Saves participant data to csv with pandas"""
        if not self.participants:
            return
            
        data = []
        for name, info in self.participants.items():
            data.append({
                'Name': name,
                'Resistence': info['Scores'][0],
                'Strength': info['Scores'][1],
                'Velocity': info['Scores'][2],
                'Resistence_Difficulty': info['Difficulties'][0],
                'Strength_Difficulty': info['Difficulties'][1],
                'Velocity_Difficulty': info['Difficulties'][2],
                'Final_Punctuation': info['Final punctuation'],
                'Qualified': 'Yes' if info['Qualified?'] else 'No'
            })
        
        try:
            pd.DataFrame(data).to_csv(self.csv_file, index=False)
        except Exception as e:
            raise Exception(f"CSV save failed: {str(e)}")

    def register_athlete(self, name, resistance, strength, velocity):
        """Registers an athlete."""
        """Register a new athlete with automatic CSV saving"""
        difficulties = {
            'Resistence': round(random.uniform(1.0, 1.3), 1),
            'Strength': round(random.uniform(1.0, 1.3), 1),
            'Velocity': round(random.uniform(1.0, 1.3), 1)
        }
        
        scores = [resistance, strength, velocity]
        difficulties_list = [difficulties['Resistence'], difficulties['Strength'], difficulties['Velocity']]

        fixed_sum = sum(s * d for s, d in zip(scores, difficulties_list)) #The modified sum for the final punctuation
        final_score = round(fixed_sum / sum(difficulties_list))
        qualified = final_score >= 70
        
        self.participants[name] = {'Scores': scores, 'Difficulties': difficulties_list,
            'Final punctuation': final_score, 'Qualified?': qualified}
        
        try:
            self.save_to_csv()
            return final_score, qualified
        except Exception as e:
            if name in self.participants:
                del self.participants[name]
            raise e

    def get_general_report_data(self):
        """Gives all information to display the general report."""
        if not self.participants: #Checks if there are athletes already registered
            return None
        
        data = {'Name': [], 'Final scores': [], 'Qualified': []}

        for name, info in self.participants.items():
            data['Name'].append(name)
            data['Final scores'].append(info['Final punctuation'])
            data['Qualified'].append('Yes' if info['Qualified?'] else 'No')
        
        df = pd.DataFrame(data)
        
        stats = {
            'average_score': df['Final scores'].mean(),
            'qualified_count': sum(df['Qualified'] == 'Yes'),
            'not_qualified_count': sum(df['Qualified'] == 'No'),
            'correlation_matrix': None,
            'pie_chart': None,
            'stats_description': df['Final scores'].describe().to_dict(),
            'correlation_plot': None
        }
        
        scores_df = pd.DataFrame([p['Scores'] for p in self.participants.values()], 
                                columns=['Resistence', 'Strength', 'Velocity'])  
        corr_matrix = scores_df.corr()
        stats['correlation_matrix'] = corr_matrix
        
        fig, ax = plt.subplots(figsize=(6, 4))
        cax = ax.matshow(corr_matrix, cmap='plasma')
        fig.colorbar(cax)

        ax.set_xticks(range(len(corr_matrix.columns)))
        ax.set_yticks(range(len(corr_matrix.columns)))
        ax.set_xticklabels(corr_matrix.columns, rotation=45)
        ax.set_yticklabels(corr_matrix.columns)
        
        for i in range(len(corr_matrix.columns)):
            for j in range(len(corr_matrix.columns)):
                ax.text(j, i, f"{corr_matrix.iloc[i, j]:.2f}",
                    ha="center", va="center", color="white")
    
        corr_buf = io.BytesIO()
        plt.savefig(corr_buf, format='png', bbox_inches='tight', dpi=100)
        corr_buf.seek(0)
        stats['correlation_plot'] = Image.open(corr_buf)
        plt.close()
        
        fig, ax = plt.subplots() #Sets up a clean chunck for my chart
        ax.pie([stats['qualified_count'], stats['not_qualified_count']],
            labels=['Qualified', 'Non-Qualified'],
            autopct='%1.1f%%') #Rounds to the first decimal and ad "%" icon
        ax.set_title('Qualified proportions')  
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        stats['pie_chart'] = Image.open(buf)
        plt.close()
        
        return df, stats

    def get_individual_report_data(self, name):
        """Gives all information to display an individual report by name."""
        
        if name not in self.participants:
            return None
            
        athlete = self.participants[name]
        tests = ['Resistence', 'Strength', 'Velocity'] 

        fig, (hst1, hst2, hst3) = plt.subplots(1, 3, figsize=(10, 5))

        hst1.bar(tests, athlete['Scores'])
        hst1.set_title('Punctuation by test') 
        hst1.set_ylim(0, 100)

        hst2.bar(tests, athlete['Difficulties'])
        hst2.set_title('Difficulties by test')
        hst2.set_ylim(1.0, 1.3)

        final_punctuation = [s * d for s, d in zip(athlete['Scores'], athlete['Difficulties'])]
        hst3.bar(tests, final_punctuation)
        hst3.set_title('Final punctuation')

        buff = io.BytesIO()
        plt.savefig(buff, format='png')
        buff.seek(0)
        histograms = Image.open(buff)
        plt.close()

        return {
            'name': name,
            'final_score': athlete['Final punctuation'],
            'qualified': athlete['Qualified?'],
            'histograms': histograms,
            'scores': athlete['Scores'],
            'difficulties': athlete['Difficulties']
        }