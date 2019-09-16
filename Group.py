class Group:

    def __init__ (self, ID, name, num_vols):
        self.num_vols = num_vols
        self.jobsites = []
        self.name = name
        self.ID = ID
        
    def add_jobsite (self, jobsite):
        self.jobsites.append(jobsite)

    def get_ID (self):
        return self.ID

    def get_num_vols (self):
        return self.num_vols

    def get_jobsites (self):
        return self.jobsites 

    def get_name (self):
        return self.name

    def __str__ (self):
        return str(self.name) + " volunteers: " + str(self.num_vols)

    def __lt__ (self, other):
        return self.num_vols < other.num_vols
    
    def __gt__ (self, other):
        return self.num_vols > other.num_vols