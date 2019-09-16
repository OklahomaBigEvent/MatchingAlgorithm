class Jobsite:
    
    def __init__ (self, name, num_vols_requested, ID=None):
        self.num_vols_requested = num_vols_requested
        self.groups = []
        self.name = name
        self.ID = ID

    def add_group (self, group):
        self.groups.append(group)

    def get_num_vols_requested (self):
        return self.num_vols_requested

    def get_groups (self):
        return self.groups 

    def get_name (self):
        return self.name

    def get_ID (self):
        return self.ID

    def get_fill_percent (self):
        vols_assigned = 0
        vols_requested = 0
        for group in self.groups:
            vols_assigned += group.get_num_vols()
        if len(self.groups) == 1:
            for jobsite in group.get_jobsites():
                vols_requested += jobsite.get_num_vols_requested()
        else:
            vols_requested = self.num_vols_requested
        return vols_assigned/vols_requested

    def get_num_vols_assigned (self):
        num_vols_assigned = 0
        if len(self.groups) > 1:
            for group in self.groups:
                num_vols_assigned += group.get_num_vols()
        elif self == self.groups[len(self.groups) - 1]:
            num_vols_assigned =  self.groups[0].get_num_vols()
            for jobsite in self.groups[0].get_jobsites():
                num_vols_assigned -= jobsite.get_num_vols_assigned()
        else:
            num_vols_assigned = int(self.get_fill_percent() * self.groups[0].get_num_vols()/len(self.groups[0].get_jobsites()))
        return num_vols_assigned

    def __str__ (self):
        to_return = str(self.ID) + ", " + str(self.name) + ", fill percent: " + str(self.get_fill_percent()) + " volunteers requested: " + str(self.num_vols_requested) + "\n"
        for group in self.groups:
            to_return += "\t" + str(group) + "\n"
        return to_return

    def __lt__ (self, other):
        return self.num_vols_requested < other.get_num_vols_requested()

    # Annie Rock sucks eggs
    def __gt__ (self, other):
        return self.num_vols_requested > other.get_num_vols_requested()
            
