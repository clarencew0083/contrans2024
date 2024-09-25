import numpy as np
import pandas as pd
import os
import dotenv
import requests
import json


class contrans:
    def __init__(self):
        """
        Initialize the contrans object.

        Gets the value of the 'mypassword' environment variable, which is
        expected to contain the password for the database.
        """
        self.mypassword = os.getenv('mypassword')
        self.congresskey = os.getenv('congresskey')
        self.newskey = os.getenv('newskey')

    def get_votes(self):

        """
        Get the House of Representatives 118th Congress vote data.

        Downloads the House of Representatives 118th Congress vote data from
        voteview.com and returns it as a pandas DataFrame.

        Parameters
        ----------
        None

        Returns
        -------
        pd.DataFrame
            A pandas DataFrame containing the vote data. The columns are
            'legislator', 'party', 'state', 'district', 'vote', 'date',
            'category', 'bill', 'description', 'result', 'president',
            'president_support', 'nominate_dim1', 'nominate_dim2', and
            'congress'.
        """
        url = 'https://voteview.com/static/data/out/votes/H118_votes.csv'
        votes = pd.read_csv(url)
        return votes
    
    def get_ideology(self):
        """
        Get the ideology data for the 118th Congress.

        Downloads the ideology data for the 118th Congress from voteview.com
        and returns it as a pandas DataFrame.

        Parameters
        ----------
        None

        Returns
        -------
        pd.DataFrame
            A pandas DataFrame containing the ideology data. The columns are
            'legislator', 'party', 'state', 'district', 'nominate_dim1',
            'nominate_dim2', 'congress', and 'chamber'.
        """
        url = url = 'https://voteview.com/static/data/out/members/H118_members.csv'
        members = pd.read_csv(url)
        return members
    
    def get_useragent(self):
        url = 'https://httpbin.org/user-agent'
        r = requests.get(url)
        useragent = json.loads(r.text)['user-agent']
        return useragent
    
    def make_headers(self, 
                    email='dnh9rs@virginia.edu'):
        useragent = self.get_useragent(),
        headers = {
            'User-Agent': useragent,
            'From': email
        }
        return headers
    
    def get_bioguideIDs(self):
        params = {'api_key': self.congresskey}
        headers = self.make_headers()
        root = 'https://api.congress.gov/v3/'
        endpoint = '/member'
        r = requests.get(root + endpoint, 
                         params=params,
                         )
        bio_df = pd.json_normalize(r.json(), record_path=['members'])
        bio_df = bio_df[['name', 'state', 'district', 'bioguideId']]

        return bio_df