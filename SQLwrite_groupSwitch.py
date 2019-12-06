from sqlalchemy import Column, String, Integer, Date, Boolean, ForeignKey, Table
from sqlalchemy.orm import relationship, backref
from base import Base # class extends to the base class as defined in the base.py module

# group to jobsite will be a Many to Many relationship, where a group can have many jobsites,
# and an jobsite can have many groups

groups_volunteers_association = Table( # table connects rows of 'groups' and rows of 'volunteers'
    'groups_volunteers', Base.metadata,
    Column('group_id', Integer, ForeignKey('group.id')),
    Column('volunteer_id', Integer, ForeignKey('volunteer.id'))
)

class Group(Base):
    __tablename__ = 'Groups' # indicates the name of the table that will support this class

    groupName = Column(String(length=60), primary_key=True) # represents the primary key in the table
    groupLeaderId = Column(Integer(length=9)) # groupLeaderID of type Integer
    jobsiteId = Column(Integer(length=3)) # jobsiteID of type Integer
    volunteers = relationship("Volunteer", secondary=groups_volunteers_association, backref="groups") 
    # 'volunteers' property is added to 'Group', with 
    # 'groups_volunteers_association' as the intermediary table

    def __init__(self, groupLeaderId, jobsiteId):
        self.groupLeaderId = groupLeaderId
        self.jobsiteId = jobsiteId

class Volunteer(Base):
    __tablename__ = 'actors'

    studentId = Column(Integer(length=9), primary_key=True)
    firstName = Column(String(length=200))
    lastName = Column(String(length=200))
    email = Column(String(length=200))
    phoneNumber = Column(String(length=25))
    groupName = Column(String(length=200))
    tshirtSize = Column(String(length=20))
    
    def __init__(self, firstName, lastName, email, phoneNumber, groupName, tshirtSize):
        self.firstName = firstName
        self.lastName = lastName
        self.email = email
        self.phoneNumber = phoneNumber
        self.groupName = groupName
        self.tshirtSize = tshirtSize
        
class Jobsite(Base):
    __tablename__ = 'jobsites'

    jobsiteId = Column(Integer(length=3), primary_key=True)
    jobsiteName = Column(String(length=200))
    streetAddress = Column(String(length=200))
    city = Column(String(length=200))
    zipCode = Column(Integer(length=5))
    email = Column(String(length=200))
    phoneNumber = Column(String(length=20))
    
    def __init__(jobsiteName, streetAddress, city, zipCode, email, phoneNumber):
        self.jobsiteName = jobsiteName
        self.streetAddress = streetAddress
        self.city = city
        self.zipCode = zipCode
        self.email = email
        self.phoneNumber = phoneNumber

# now, imported Table, ForeignKey, and relationship

# groupLeaderID and jobsiteID
# groupleader id from volunteers to orgs
# groupID wihtin volunteers to group (campus) orgs. GroupleaderID within org table and groupID within volunteers table
# between group and jobsite via jobsite ID
# key means primary key
# hashtag means integer (data type)