import numpy as np
import pandas as pd
import os
import dotenv
import requests
import json
from bs4 import BeautifulSoup


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
        self.us_state_to_abbrev = {
                "Alabama": "AL","Alaska": "AK","Arizona": "AZ","Arkansas": "AR",
                "California": "CA","Colorado": "CO","Connecticut": "CT","Delaware": "DE",
                "Florida": "FL","Georgia": "GA","Hawaii": "HI",
                "Idaho": "ID","Illinois": "IL","Indiana": "IN","Iowa": "IA",
                "Kansas": "KS","Kentucky": "KY","Louisiana": "LA",
                "Maine": "ME","Maryland": "MD","Massachusetts": "MA",
                "Michigan": "MI","Minnesota": "MN","Mississippi": "MS",
                "Missouri": "MO","Montana": "MT","Nebraska": "NE",
                "Nevada": "NV","New Hampshire": "NH","New Jersey": "NJ",
                "New Mexico": "NM","New York": "NY","North Carolina": "NC",
                "North Dakota": "ND","Ohio": "OH","Oklahoma": "OK",
                "Oregon": "OR","Pennsylvania": "PA","Rhode Island": "RI",
                "South Carolina": "SC","South Dakota": "SD","Tennessee": "TN",
                "Texas": "TX","Utah": "UT","Vermont": "VT",
                "Virginia": "VA","Washington": "WA","West Virginia": "WV",
                "Wisconsin": "WI","Wyoming": "WY","District of Columbia": "DC",
                "American Samoa": "AS","Guam": "GU","Northern Mariana Islands": "MP",
                "Puerto Rico": "PR","United States Minor Outlying Islands": "UM",
                "Virgin Islands": "VI"
                }

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
    
    def get_bioguideIDs(self, congress=118):
        params = {'api_key': self.congresskey,
                  'limit': 1}
        headers = self.make_headers()
        root = 'https://api.congress.gov/v3/'
        endpoint = f'/member/congress/{congress}'
        r = requests.get(root + endpoint, 
                         params=params,
                         )
        totalrecords = r.json()['pagination']['count']
        params['limit'] = 250
        j = 0
        bio_df = pd.DataFrame()
        while j < totalrecords:
            params['offset'] = j
            r = requests.get(root + endpoint, 
                             params=params,
                             )
            records = pd.json_normalize(r.json()['members'])
            bio_df = pd.concat([bio_df, records], ignore_index=True)
            j = j + 250
        return bio_df
    
    def get_bioguide(self, name, state=None, district=None):
            
            members = self.get_bioguideIDs() # replace with SQL query

            members['name'] = members['name'].str.lower().str.strip()
            name = name.lower().strip()

            tokeep = [name in x for x in members['name']]
            members = members[tokeep]

            if state is not None:
                    members = members.query('state == @state')

            if district is not None:
                    members = members.query('district == @district')
            
            return members.reset_index(drop=True)
        #bio_df = pd.json_normalize(r.json(), record_path=['members'])
        #bio_df = pd.json_normalize(records)
        #bio_df = bio_df[['name', 'state', 'district', 'partyName', 'bioguideId']]

    
    def get_bioguide(self, name, state=None, district=None):

        members = self.get_bioguideIDs() # replace with SQL query

        members['name'] = members['name'].str.lower().str.strip()
        name = name.lower().strip()

        tokeep = [name in x for x in members['name']]
        members = members[tokeep]

        if state is not None:
            members = members.query('state == @state')
        if district is not None:
            members = members.query('district == @district')

        return members.reset_index(drop=True)
    

    def get_sponseredLegislation(self, bioguideID):

        params = {'api_key': self.congresskey,
                  'limit': 1}
        headers = self.make_headers()
        root = 'https://api.congress.gov/v3/'
        endpoint = f'/member/{bioguideID}/sponsored-legislation'
        r = requests.get(root + endpoint, 
                         params=params,
                         )
        totalrecords = r.json()['pagination']['count']
        params['limit'] = 250
        j = 0
        bills_list = []
        while j < totalrecords:
            params['offset'] = j
            r = requests.get(root + endpoint, 
                             params=params,
                             #headers=headers,
                             )
            records = r.json()['sponsoredLegislation']
            bills_list += records
            j = j + 250

        return bills_list

    def get_billdata(self, billurl):
        r = requests.get(billurl,
                        params= {'api_key': self.congresskey})
        bill_json = json.loads(r.text)
        texturl = bill_json['bill']['textVersions']['url']
        r = requests.get(texturl,
                    params= {'api_key': self.congresskey})

        toscrape = json.loads(r.text)['textVersions'][0]['formats'][0]['url']

        r = requests.get(toscrape)
        mysoup = BeautifulSoup(r.text, 'html.parser')
        billtext = mysoup.text
        bill_json['bill_text'] = billtext
        return bill_json
    
    def make_cand_table(self, members):
            # members is output of get_terms()
            replace_map = {'Republican': 'R','Democratic': 'D','Independent': 'I'}
            members['partyletter'] = members['partyName'].replace(replace_map)
            members['state'] = members['state'].replace(self.us_state_to_abbrev)
            members['district'] = members['district'].fillna(0)
            members['district'] = members['district'].astype('int').astype('str')
            members['district'] = ['0' + x if len(x) == 1 else x for x in members['district']]
            members['district'] = [x.replace('00', 'S') for x in members['district']]
            members['DistIDRunFor'] = members['state']+members['district']
            members['lastname']= [x.split(',')[0] for x in members['name']]
            members['firstname']= [x.split(',')[1] for x in members['name']]
            members['name2'] = [ y.strip() + ' (' + z.strip() + ')' 
                            for y, z in 
                            zip(members['lastname'], members['partyletter'])]
            
            cands = pd.read_csv('data/cands22.txt', quotechar="|", header=None)
            cands.columns = ['Cycle', 'FECCandID', 'CID','FirstLastP',
                            'Party','DistIDRunFor','DistIDCurr',
                            'CurrCand','CycleCand','CRPICO','RecipCode','NoPacs']
            cands['DistIDRunFor'] = [x.replace('S0', 'S') for x in cands['DistIDRunFor']]
            cands['DistIDRunFor'] = [x.replace('S1', 'S') for x in cands['DistIDRunFor']]
            cands['DistIDRunFor'] = [x.replace('S2', 'S') for x in cands['DistIDRunFor']]
            cands['name2'] = [' '.join(x.split(' ')[-2:]) for x in cands['FirstLastP']]
            cands = cands[['CID', 'name2', 'DistIDRunFor']].drop_duplicates(subset=['name2', 'DistIDRunFor'])
            crosswalk = pd.merge(members, cands, 
                    left_on=['name2', 'DistIDRunFor'],
                    right_on=['name2', 'DistIDRunFor'],
                    how = 'left')
            return crosswalk
    
    def terms_df(self, members):
        termsDF = pd.DataFrame()
        for index, row in members.iterrows():
            bioguide_id = row['bioguideId']
            terms = row['terms.item']
            df = pd.DataFrame.from_records(terms)
            df['bioguideId'] = bioguide_id
            termsDF = pd.concat([termsDF, df], ignore_index=True)
        members = members.drop('terms.item', axis=1)
        return termsDF, members
    
    ### Memebers for building the 3NF relational DB tables

    def make_members_df(self, members, ideology):
        '''
        members should be the output of get_bioguideIDs()
        with terms removed by get_terms()
        augmented with contributions by make_cand_table()
        ideology should be the output of get_ideology()
        '''
        members_df = pd.merge(members, ideology, 
                              left_on='bioguideId',
                              right_on='bioguide_id', 
                              how = 'left')
        return members_df
    
    def make_terms_df(self):
        pass

    def make_votes_df(self):
        pass

    def make_aggreement_df(self):
         pass
    

            

