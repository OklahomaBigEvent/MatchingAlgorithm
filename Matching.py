from Group import Group
from Jobsite import Jobsite
import copy
import itertools
import xlwt 
from xlwt import Workbook 
import xlrd
import sys

jobsites_from_file = []
groups_from_file = []
unassigned_jobsites = []
unassigned_groups = []
assigned_jobsites = []
assigned_groups = []
FILL_PERCENT = 1

# TODO: can all be deleted after debugging
def print_matches():
    for jobsite_index in range(len(assigned_jobsites)):
        print(assigned_jobsites[jobsite_index])  
def print_unassigned():
    for jobsite_index in range(len(unassigned_jobsites)):
        print(unassigned_jobsites[jobsite_index]) 
    for group_index in range(len(unassigned_groups)):
        print(unassigned_groups[group_index])

# matching is done favoring big groups to small jobsites
def match1to1_over(leniency):
    # start at smallest jobsite
    jobsite_index = 0
    while jobsite_index < len(unassigned_jobsites):
        # print(unassigned_jobsites[jobsite_index], "\n")
        # calculate the minimum and maximum volunteers from groups that'll satisfy jobsite
        min_fill = unassigned_jobsites[jobsite_index].get_num_vols_requested() * (FILL_PERCENT - leniency)
        max_fill = unassigned_jobsites[jobsite_index].get_num_vols_requested() * (FILL_PERCENT + leniency)
        # start at largest group
        group_index = len(unassigned_groups) - 1
        # while the group is too big
        while  group_index >= 0 and unassigned_groups[group_index].get_num_vols() > max_fill:
            # print("\t", unassigned_groups[group_index], "\n")
            group_index -= 1
        # if it's a match!
        if group_index >= 0 and unassigned_groups[group_index].get_num_vols() >= min_fill:
            # print("\t", unassigned_groups[group_index], "\n")
            unassigned_jobsites[jobsite_index].add_group(unassigned_groups[group_index])
            unassigned_groups[group_index].add_jobsite(unassigned_jobsites[jobsite_index])

            assigned_jobsites.append(copy.deepcopy(unassigned_jobsites[jobsite_index]))
            del unassigned_jobsites[jobsite_index]

            assigned_groups.append(copy.deepcopy(unassigned_groups[group_index]))
            del unassigned_groups[group_index]
        # if not a match, increment jobsite
        else:
            # print(unassigned_jobsites[jobsite_index], "\n")
            jobsite_index += 1
def match2to1_over(leniency):
    # start from smallest jobsite
    jobsite_index = 0
    while jobsite_index < len(unassigned_jobsites) and len(unassigned_groups) >= 2:
        # calculate the minimum and maximum volunteers from groups that'll satisfy jobsite
        min_fill = unassigned_jobsites[jobsite_index].get_num_vols_requested() * (FILL_PERCENT - leniency) 
        max_fill = unassigned_jobsites[jobsite_index].get_num_vols_requested() * (FILL_PERCENT + leniency) 
        # if we can tell this jobsite will never be satisfied from the get-go because it is too small or big
        if (unassigned_groups[0].get_num_vols() + unassigned_groups[1].get_num_vols() > max_fill
                or unassigned_groups[len(unassigned_groups) - 1].get_num_vols() + unassigned_groups[len(unassigned_groups) - 2].get_num_vols() < min_fill):
            # print(unassigned_jobsites[jobsite_index], "\n")
            jobsite_index += 1
            continue
        # print(unassigned_jobsites[jobsite_index], "\n")
        group_index_1 = len(unassigned_groups) - 1
        # if group is too large to even go under the max with the smallest group
        while group_index_1 >= 1 and unassigned_groups[group_index_1].get_num_vols() + unassigned_groups[0].get_num_vols() > max_fill:
            # print("\t", unassigned_groups[group_index_1], "\n")
            group_index_1 -= 1
        # if group is out of range or is too small to be over the min
        if group_index_1 < 1 or unassigned_groups[group_index_1].get_num_vols() + unassigned_groups[group_index_1 - 1].get_num_vols() < min_fill:
            jobsite_index += 1
            continue
        # go through each group
        while jobsite_index < len(unassigned_jobsites):
            # print("\t", unassigned_groups[group_index_1], "\n")
            group_index_2 = group_index_1 - 1
            while group_index_2 >= 0 and unassigned_groups[group_index_1].get_num_vols() + unassigned_groups[group_index_2].get_num_vols() > max_fill:
                # print("\t\t", unassigned_groups[group_index_2], "\n")
                group_index_2 -= 1
            if group_index_2 >= 0 and unassigned_groups[group_index_1].get_num_vols() + unassigned_groups[group_index_2].get_num_vols() >= min_fill:
                # print("\t\t", unassigned_groups[group_index_2], "\n")
                unassigned_jobsites[jobsite_index].add_group(unassigned_groups[group_index_1])
                unassigned_jobsites[jobsite_index].add_group(unassigned_groups[group_index_2])
                unassigned_groups[group_index_1].add_jobsite(unassigned_jobsites[jobsite_index])
                unassigned_groups[group_index_2].add_jobsite(unassigned_jobsites[jobsite_index])

                assigned_jobsites.append(copy.deepcopy(unassigned_jobsites[jobsite_index]))
                del unassigned_jobsites[jobsite_index]

                assigned_groups.append(copy.deepcopy(unassigned_groups[group_index_1]))
                assigned_groups.append(copy.deepcopy(unassigned_groups[group_index_2]))
                del unassigned_groups[group_index_1]
                del unassigned_groups[group_index_2]
                break
            group_index_1 -= 1
            if group_index_1 < 1:
                jobsite_index += 1
                break
def match1to2_over(leniency):
    # start from biggest group
    group_index = len(unassigned_groups) - 1
    while group_index >= 0 and len(unassigned_jobsites) >= 2 and unassigned_groups[group_index].get_num_vols() >= 30:
        # calculate the minimum and maximum volunteers requested from jobsites that'll satisfy group
        min_fill = unassigned_groups[group_index].get_num_vols() / (FILL_PERCENT + leniency)
        max_fill = unassigned_groups[group_index].get_num_vols() / (FILL_PERCENT - leniency)
        # if we can tell this group will never be satisfied from the get-go because it is too small or big
        if (unassigned_jobsites[len(unassigned_jobsites) - 1].get_num_vols_requested() + unassigned_jobsites[len(unassigned_jobsites) - 2].get_num_vols_requested() < min_fill
                or unassigned_jobsites[0].get_num_vols_requested() + unassigned_jobsites[1].get_num_vols_requested() > max_fill):
            # print(unassigned_groups[group_index], "\n")
            group_index -= 1
            continue
        # print(unassigned_groups[group_index], "\n")
        # start from smallest jobsite
        jobsite_index_1 = 0
        while jobsite_index_1 < len(unassigned_jobsites) - 1 and unassigned_jobsites[jobsite_index_1].get_num_vols_requested() < 15:
            jobsite_index_1 += 1
        # if jobsite is too small to even surpass max with the biggest jobsite
        while jobsite_index_1 < len(unassigned_jobsites) - 1 and unassigned_jobsites[jobsite_index_1].get_num_vols_requested() + unassigned_jobsites[len(unassigned_jobsites) - 1].get_num_vols_requested() < min_fill:
            # print("\t", unassigned_jobsites[jobsite_index_1], "\n")
            jobsite_index_1 += 1
        # if jobsite is out of range or is too big to be under the minimum with the smallest jobsite
        if jobsite_index_1 >= len(unassigned_jobsites) - 1 or unassigned_jobsites[jobsite_index_1].get_num_vols_requested() + unassigned_jobsites[jobsite_index_1 + 1].get_num_vols_requested() > max_fill:
            group_index -= 1
            continue
        # go through each jobsite
        while jobsite_index_1 < len(unassigned_jobsites):
            # print("\t", unassigned_jobsites[jobsite_index_1], "\n")
            jobsite_index_2 = jobsite_index_1 + 1
            # go through each second jobsite assessing if big enough
            while jobsite_index_2 < len(unassigned_jobsites) and unassigned_jobsites[jobsite_index_1].get_num_vols_requested() + unassigned_jobsites[jobsite_index_2].get_num_vols_requested() < min_fill:
                # print("\t\t", unassigned_jobsites[jobsite_index_2], "\n")
                jobsite_index_2 += 1
            # if it's a match!
            if jobsite_index_2 < len(unassigned_jobsites) and unassigned_jobsites[jobsite_index_1].get_num_vols_requested() + unassigned_jobsites[jobsite_index_2].get_num_vols_requested() <= max_fill:
                # print("\t\t", unassigned_jobsites[jobsite_index_2], "\n")
                unassigned_jobsites[jobsite_index_1].add_group(unassigned_groups[group_index])
                unassigned_jobsites[jobsite_index_2].add_group(unassigned_groups[group_index])
                unassigned_groups[group_index].add_jobsite(unassigned_jobsites[jobsite_index_1])
                unassigned_groups[group_index].add_jobsite(unassigned_jobsites[jobsite_index_2])

                assigned_jobsites.append(copy.deepcopy(unassigned_jobsites[jobsite_index_1]))
                assigned_jobsites.append(copy.deepcopy(unassigned_jobsites[jobsite_index_2]))
                del unassigned_jobsites[jobsite_index_2]
                del unassigned_jobsites[jobsite_index_1]

                assigned_groups.append(copy.deepcopy(unassigned_groups[group_index]))
                del unassigned_groups[group_index]
                group_index -= 1
                break
            # if not a match, move to next first jobsite 
            jobsite_index_1 += 1
            # if first jobsite isn't viable index
            if jobsite_index_1 >= len(unassigned_jobsites) - 1:
                group_index -= 1
                break
def match3to1_over(leniency):
    flag = False
    # start from smallest jobsite
    jobsite_index = 0
    while jobsite_index < len(unassigned_jobsites) and len(unassigned_groups) >= 3:
        # calculate the minimum and maximum volunteers from groups that'll satisfy jobsite
        min_fill = unassigned_jobsites[jobsite_index].get_num_vols_requested() * (FILL_PERCENT - leniency) 
        max_fill = unassigned_jobsites[jobsite_index].get_num_vols_requested() * (FILL_PERCENT + leniency) 
        # if we can tell this jobsite will never be satisfied from the get-go because it is too big or small
        if (unassigned_groups[0].get_num_vols() + unassigned_groups[1].get_num_vols() + unassigned_groups[2].get_num_vols() > max_fill
                or unassigned_groups[len(unassigned_groups) - 1].get_num_vols() + unassigned_groups[len(unassigned_groups) - 2].get_num_vols() + unassigned_groups[len(unassigned_groups) - 3].get_num_vols() < min_fill):
            # print(unassigned_jobsites[jobsite_index], "\n")
            jobsite_index += 1
            continue
        # print(unassigned_jobsites[jobsite_index], "\n")
        # start from largest group
        group_index_1 = len(unassigned_groups) - 1
        # if group is too large to even go under the max with the 2 smallest groups
        while group_index_1 >= 2 and unassigned_groups[group_index_1].get_num_vols() + unassigned_groups[1].get_num_vols() + unassigned_groups[0].get_num_vols() > max_fill:
            # print("\t", unassigned_groups[group_index_1], "\n")
            group_index_1 -= 1
        # if group is out of range or is too small to be over the min
        if group_index_1 < 2 or unassigned_groups[group_index_1].get_num_vols() + unassigned_groups[group_index_1 - 1].get_num_vols() + unassigned_groups[group_index_1 - 2].get_num_vols() < min_fill:
            jobsite_index += 1
            continue
        # go through each group
        while jobsite_index < len(unassigned_jobsites):
            # print("\t", unassigned_groups[group_index_1], "\n")
            group_index_2 = group_index_1 - 1
            # if second group is too large
            while group_index_2 >= 1 and unassigned_groups[group_index_1].get_num_vols() + unassigned_groups[group_index_2].get_num_vols() + unassigned_groups[0].get_num_vols() > max_fill:
                # print("\t\t", unassigned_groups[group_index_2], "\n")
                group_index_2 -= 1
            # if second group is out of range or is too small
            if group_index_2 < 1 or unassigned_groups[group_index_1].get_num_vols() + unassigned_groups[group_index_2].get_num_vols() + unassigned_groups[group_index_2 - 1].get_num_vols() < min_fill:
                group_index_1 -= 1
                if group_index_1 < 2:
                    jobsite_index += 1
                    break
                continue
            # go through each second group
            while group_index_2 >= 0 and group_index_1 >= 0 and group_index_1 < len(unassigned_groups) and jobsite_index < len(unassigned_jobsites):
                # print("\t\t", unassigned_groups[group_index_2], "\n")
                group_index_3 = group_index_2 - 1
                # go through each third group assessing if small enough
                while group_index_3 >= 0 and unassigned_groups[group_index_1].get_num_vols() + unassigned_groups[group_index_2].get_num_vols() + unassigned_groups[group_index_3].get_num_vols() > max_fill:
                    # print("\t\t\t", unassigned_groups[group_index_3], "\n")
                    group_index_3 -= 1
                # it's a match!
                if group_index_3 >= 0 and unassigned_groups[group_index_1].get_num_vols() + unassigned_groups[group_index_2].get_num_vols() + unassigned_groups[group_index_3].get_num_vols() >= min_fill:
                    # print("\t\t\t", unassigned_groups[group_index_3], "\n")
                    unassigned_jobsites[jobsite_index].add_group(unassigned_groups[group_index_1])
                    unassigned_jobsites[jobsite_index].add_group(unassigned_groups[group_index_2])
                    unassigned_jobsites[jobsite_index].add_group(unassigned_groups[group_index_3])
                    unassigned_groups[group_index_1].add_jobsite(unassigned_jobsites[jobsite_index])
                    unassigned_groups[group_index_2].add_jobsite(unassigned_jobsites[jobsite_index])
                    unassigned_groups[group_index_3].add_jobsite(unassigned_jobsites[jobsite_index])

                    assigned_jobsites.append(copy.deepcopy(unassigned_jobsites[jobsite_index]))
                    del unassigned_jobsites[jobsite_index]

                    assigned_groups.append(copy.deepcopy(unassigned_groups[group_index_1]))
                    assigned_groups.append(copy.deepcopy(unassigned_groups[group_index_2]))
                    assigned_groups.append(copy.deepcopy(unassigned_groups[group_index_3]))
                    del unassigned_groups[group_index_1] 
                    del unassigned_groups[group_index_2]
                    del unassigned_groups[group_index_3]  
                    flag = True
                    break 
                # if not a match, move to next second jobsite
                group_index_2 -= 1
                # if second group is not a viable index
                if group_index_2 < 1:
                    group_index_1 -= 1
                    # if first group is not a viable index
                    if group_index_1 < 2:
                        jobsite_index += 1
                        flag = True
                    break
            if flag:
                flag = False
                break
def match1to3_over(leniency):
    flag = False
    # start from biggest group
    group_index = len(unassigned_groups) - 1
    while group_index >= 0 and len(unassigned_jobsites) >= 3 and unassigned_groups[group_index].get_num_vols() >= 45:
        # calculate the minimum and maximum volunteers requested from jobsites that'll satisfy group
        min_fill = unassigned_groups[group_index].get_num_vols() / (FILL_PERCENT + leniency)
        max_fill = unassigned_groups[group_index].get_num_vols() / (FILL_PERCENT - leniency)
        # if we can tell this group will never be satisfied from the get-go because it is too small or big
        if (unassigned_jobsites[len(unassigned_jobsites) - 1].get_num_vols_requested() + unassigned_jobsites[len(unassigned_jobsites) - 1].get_num_vols_requested() + unassigned_jobsites[len(unassigned_jobsites) - 1].get_num_vols_requested() < min_fill
                or unassigned_jobsites[0].get_num_vols_requested() + unassigned_jobsites[1].get_num_vols_requested() + unassigned_jobsites[2].get_num_vols_requested() > max_fill):
            # print(unassigned_groups[group_index], "\n")
            group_index -= 1
            continue
        # print(unassigned_groups[group_index], "\n")
        # start from smallest jobsite
        jobsite_index_1 = 0
        while jobsite_index_1 < len(unassigned_jobsites) - 2 and unassigned_jobsites[jobsite_index_1].get_num_vols_requested() < 15:
            jobsite_index_1 += 1
        # if jobsite is too small to even surpass max with the 2 biggest jobsites
        while jobsite_index_1 < len(unassigned_jobsites) - 2 and unassigned_jobsites[jobsite_index_1].get_num_vols_requested() + unassigned_jobsites[len(unassigned_jobsites) - 1].get_num_vols_requested() + unassigned_jobsites[len(unassigned_jobsites) - 2].get_num_vols_requested() < min_fill:
            # print("\t", unassigned_jobsites[jobsite_index_1], "\n")
            jobsite_index_1 += 1
        # if jobsite is out of range or is too big to be under the minimum with the 2 smallest jobsites
        if jobsite_index_1 >= len(unassigned_jobsites) - 2 or unassigned_jobsites[jobsite_index_1].get_num_vols_requested() + unassigned_jobsites[jobsite_index_1 + 1].get_num_vols_requested() + unassigned_jobsites[jobsite_index_1 + 2].get_num_vols_requested() > max_fill:
            group_index -= 1
            continue
        # go through each jobsite
        while jobsite_index_1 < len(unassigned_jobsites) - 2:
            # print("\t", unassigned_jobsites[jobsite_index_1], "\n")
            jobsite_index_2 = jobsite_index_1 + 1
            # if second jobsite is too small
            while jobsite_index_2 < len(unassigned_jobsites) - 1 and unassigned_jobsites[jobsite_index_1].get_num_vols_requested() + unassigned_jobsites[jobsite_index_2].get_num_vols_requested() + unassigned_jobsites[len(unassigned_jobsites) - 1].get_num_vols_requested() < min_fill:
                # print("\t\t", unassigned_jobsites[jobsite_index_2], "\n")
                jobsite_index_2 += 1
            # if second jobsite is out of range or is too big
            if jobsite_index_2 >= len(unassigned_jobsites) - 1 or unassigned_jobsites[jobsite_index_1].get_num_vols_requested() + unassigned_jobsites[jobsite_index_2].get_num_vols_requested() + unassigned_jobsites[jobsite_index_2 + 1].get_num_vols_requested() > max_fill:
                jobsite_index_1 += 1
                continue
            # go through each second jobsite
            while jobsite_index_2 < len(unassigned_jobsites) - 1:
                # print("\t\t", unassigned_jobsites[jobsite_index_2], "\n")
                jobsite_index_3 = jobsite_index_2 + 1
                # go through each third jobsite assessing if big enough
                while jobsite_index_3 < len(unassigned_jobsites) and unassigned_jobsites[jobsite_index_1].get_num_vols_requested() + unassigned_jobsites[jobsite_index_2].get_num_vols_requested() + unassigned_jobsites[jobsite_index_3].get_num_vols_requested() < min_fill:
                    # print("\t\t\t", unassigned_jobsites[jobsite_index_3], "\n")
                    jobsite_index_3 += 1
                # if it's a match!
                if jobsite_index_3 < len(unassigned_jobsites) and unassigned_jobsites[jobsite_index_1].get_num_vols_requested() + unassigned_jobsites[jobsite_index_2].get_num_vols_requested() + unassigned_jobsites[jobsite_index_3].get_num_vols_requested() <= max_fill:
                    # print("\t\t\t", unassigned_jobsites[jobsite_index_3], "\n")
                    unassigned_jobsites[jobsite_index_1].add_group(unassigned_groups[group_index])
                    unassigned_jobsites[jobsite_index_2].add_group(unassigned_groups[group_index])
                    unassigned_jobsites[jobsite_index_3].add_group(unassigned_groups[group_index])
                    unassigned_groups[group_index].add_jobsite(unassigned_jobsites[jobsite_index_1])
                    unassigned_groups[group_index].add_jobsite(unassigned_jobsites[jobsite_index_2])
                    unassigned_groups[group_index].add_jobsite(unassigned_jobsites[jobsite_index_3])

                    assigned_jobsites.append(copy.deepcopy(unassigned_jobsites[jobsite_index_1]))
                    assigned_jobsites.append(copy.deepcopy(unassigned_jobsites[jobsite_index_2]))
                    assigned_jobsites.append(copy.deepcopy(unassigned_jobsites[jobsite_index_3]))
                    del unassigned_jobsites[jobsite_index_3]
                    del unassigned_jobsites[jobsite_index_2]
                    del unassigned_jobsites[jobsite_index_1]

                    assigned_groups.append(copy.deepcopy(unassigned_groups[group_index]))
                    del unassigned_groups[group_index]
                    group_index -= 1
                    flag = True
                    break
                # if not a match, move to next second jobsite 
                jobsite_index_2 += 1
                # if second jobsite isn't viable index
                if jobsite_index_2 >= len(unassigned_jobsites) - 1:
                    jobsite_index_1 += 1
                    # if first jobsite isn't a viable index
                    if jobsite_index_1 >= len(unassigned_jobsites) - 2:
                        group_index -= 1
                        flag = True
                    break
            if flag:
                flag = False
                break
# matching is done favoring small groups to big jobsites
def match1to1_under(leniency):
    # start at largest jobsite
    jobsite_index = len(unassigned_jobsites) - 1
    while jobsite_index >= 0:
        # print(unassigned_jobsites[jobsite_index], "\n")
        # calculate the minimum and maximum volunteers from groups that'll satisfy jobsite
        min_fill = unassigned_jobsites[jobsite_index].get_num_vols_requested() * (FILL_PERCENT - leniency)
        max_fill = unassigned_jobsites[jobsite_index].get_num_vols_requested() * (FILL_PERCENT + leniency)
        # start at smallest group
        group_index = 0
        # while the group is too big
        while  group_index < len(unassigned_groups) and unassigned_groups[group_index].get_num_vols() < min_fill:
            # print("\t", unassigned_groups[group_index], "\n")
            group_index += 1
        # if it's a match!
        if group_index < len(unassigned_groups) and unassigned_groups[group_index].get_num_vols() <= max_fill:
            # print("\t", unassigned_groups[group_index], "\n")
            unassigned_jobsites[jobsite_index].add_group(unassigned_groups[group_index])
            unassigned_groups[group_index].add_jobsite(unassigned_jobsites[jobsite_index])

            assigned_jobsites.append(copy.deepcopy(unassigned_jobsites[jobsite_index]))
            del unassigned_jobsites[jobsite_index]

            assigned_groups.append(copy.deepcopy(unassigned_groups[group_index]))
            del unassigned_groups[group_index]
        jobsite_index -= 1
def match2to1_under(leniency):
    # start from smallest jobsite
    jobsite_index = len(unassigned_jobsites) - 1
    while jobsite_index >= 0 and len(unassigned_groups) >= 2:
        # calculate the minimum and maximum volunteers from groups that'll satisfy jobsite
        min_fill = unassigned_jobsites[jobsite_index].get_num_vols_requested() * (FILL_PERCENT - leniency) 
        max_fill = unassigned_jobsites[jobsite_index].get_num_vols_requested() * (FILL_PERCENT + leniency) 
        # if we can tell this jobsite will never be satisfied from the get-go because it is too small or big
        if (unassigned_groups[0].get_num_vols() + unassigned_groups[1].get_num_vols() > max_fill
                or unassigned_groups[len(unassigned_groups) - 1].get_num_vols() + unassigned_groups[len(unassigned_groups) - 2].get_num_vols() < min_fill):
            # print(unassigned_jobsites[jobsite_index], "\n")
            jobsite_index -= 1
            continue
        # print(unassigned_jobsites[jobsite_index], "\n")
        group_index_1 = 0
        # if group is too small to even go over the min with the largest group
        while group_index_1 < len(unassigned_groups) and unassigned_groups[group_index_1].get_num_vols() + unassigned_groups[len(unassigned_groups) - 1].get_num_vols() < min_fill:
            # print("\t", unassigned_groups[group_index_1], "\n")
            group_index_1 += 1
        # if group is out of range or is too big to be under the max
        if group_index_1 >= len(unassigned_groups) - 1 or unassigned_groups[group_index_1].get_num_vols() + unassigned_groups[0].get_num_vols() > max_fill:
            jobsite_index -= 1
            continue
        # go through each group
        while jobsite_index >= 0:
            # print("\t", unassigned_groups[group_index_1], "\n")
            group_index_2 = group_index_1 + 1
            while group_index_2 < len(unassigned_groups) and unassigned_groups[group_index_1].get_num_vols() + unassigned_groups[group_index_2].get_num_vols() < min_fill:
                # print("\t\t", unassigned_groups[group_index_2], "\n")
                group_index_2 += 1
            if group_index_2 < len(unassigned_groups) and unassigned_groups[group_index_1].get_num_vols() + unassigned_groups[group_index_2].get_num_vols() <= max_fill:
                # print("\t\t", unassigned_groups[group_index_2], "\n")
                unassigned_jobsites[jobsite_index].add_group(unassigned_groups[group_index_1])
                unassigned_jobsites[jobsite_index].add_group(unassigned_groups[group_index_2])
                unassigned_groups[group_index_1].add_jobsite(unassigned_jobsites[jobsite_index])
                unassigned_groups[group_index_2].add_jobsite(unassigned_jobsites[jobsite_index])

                assigned_jobsites.append(copy.deepcopy(unassigned_jobsites[jobsite_index]))
                del unassigned_jobsites[jobsite_index]

                assigned_groups.append(copy.deepcopy(unassigned_groups[group_index_1]))
                assigned_groups.append(copy.deepcopy(unassigned_groups[group_index_2]))
                del unassigned_groups[group_index_2]
                del unassigned_groups[group_index_1]
                jobsite_index -= 1
                break
            group_index_1 += 1
            if group_index_1 > len(unassigned_groups):
                jobsite_index -= 1
                break
def match1to2_under(leniency):
    # start from biggest group
    group_index = 0
    while group_index < len(unassigned_groups) and unassigned_groups[group_index].get_num_vols() < 30:
        group_index += 1
    while group_index < len(unassigned_groups) and len(unassigned_jobsites) >= 2:
        # calculate the minimum and maximum volunteers requested from jobsites that'll satisfy group
        min_fill = unassigned_groups[group_index].get_num_vols() / (FILL_PERCENT + leniency)
        max_fill = unassigned_groups[group_index].get_num_vols() / (FILL_PERCENT - leniency)
        # if we can tell this group will never be satisfied from the get-go because it is too small or big
        if (unassigned_jobsites[len(unassigned_jobsites) - 1].get_num_vols_requested() + unassigned_jobsites[len(unassigned_jobsites) - 2].get_num_vols_requested() < min_fill
                or unassigned_jobsites[0].get_num_vols_requested() + unassigned_jobsites[1].get_num_vols_requested() > max_fill):
            # print(unassigned_groups[group_index], "\n")
            group_index += 1
            continue
        # print(unassigned_groups[group_index], "\n")
        # start from smallest jobsite
        jobsite_index_1 = len(unassigned_jobsites) - 1
        while jobsite_index_1 >= 1 and unassigned_jobsites[jobsite_index_1].get_num_vols_requested() < 15:
            group_index += 1
            continue
        # if jobsite is too small to even surpass max with the biggest jobsite
        while jobsite_index_1 >= 1 and unassigned_jobsites[jobsite_index_1].get_num_vols_requested() + unassigned_jobsites[0].get_num_vols_requested() > max_fill:
            # print("\t", unassigned_jobsites[jobsite_index_1], "\n")
            jobsite_index_1 -= 1
        # if jobsite is out of range or is too big to be under the minimum with the smallest jobsite
        if jobsite_index_1 < 1 or unassigned_jobsites[jobsite_index_1].get_num_vols_requested() + unassigned_jobsites[jobsite_index_1 - 1].get_num_vols_requested() < min_fill:
            group_index += 1
            continue
        # go through each jobsite
        while jobsite_index_1 >= 1:
            # print("\t", unassigned_jobsites[jobsite_index_1], "\n")
            jobsite_index_2 = jobsite_index_1 - 1
            # go through each second jobsite assessing if small enough
            while jobsite_index_2 >= 0 and unassigned_jobsites[jobsite_index_1].get_num_vols_requested() + unassigned_jobsites[jobsite_index_2].get_num_vols_requested() > max_fill:
                # print("\t\t", unassigned_jobsites[jobsite_index_2], "\n")
                jobsite_index_2 -= 1
            # if it's a match!
            if jobsite_index_2 >= 0 and unassigned_jobsites[jobsite_index_1].get_num_vols_requested() + unassigned_jobsites[jobsite_index_2].get_num_vols_requested() >= min_fill:
                # print("\t\t", unassigned_jobsites[jobsite_index_2], "\n")
                unassigned_jobsites[jobsite_index_1].add_group(unassigned_groups[group_index])
                unassigned_jobsites[jobsite_index_2].add_group(unassigned_groups[group_index])
                unassigned_groups[group_index].add_jobsite(unassigned_jobsites[jobsite_index_1])
                unassigned_groups[group_index].add_jobsite(unassigned_jobsites[jobsite_index_2])

                assigned_jobsites.append(copy.deepcopy(unassigned_jobsites[jobsite_index_1]))
                assigned_jobsites.append(copy.deepcopy(unassigned_jobsites[jobsite_index_2]))
                del unassigned_jobsites[jobsite_index_1]
                del unassigned_jobsites[jobsite_index_2]

                assigned_groups.append(copy.deepcopy(unassigned_groups[group_index]))
                del unassigned_groups[group_index]
                break
            # if not a match, move to next first jobsite 
            jobsite_index_1 -= 1
            # if first jobsite isn't viable index
            if jobsite_index_1 < 1:
                group_index += 1
                break
def match3to1_under(leniency):
    flag = False
    # start from smallest jobsite
    jobsite_index = len(unassigned_jobsites) - 1
    while jobsite_index >= 0 and len(unassigned_groups) >= 3:
        # calculate the minimum and maximum volunteers from groups that'll satisfy jobsite
        min_fill = unassigned_jobsites[jobsite_index].get_num_vols_requested() * (FILL_PERCENT - leniency) 
        max_fill = unassigned_jobsites[jobsite_index].get_num_vols_requested() * (FILL_PERCENT + leniency) 
        # if we can tell this jobsite will never be satisfied from the get-go because it is too big or small
        if (unassigned_groups[0].get_num_vols() + unassigned_groups[1].get_num_vols() + unassigned_groups[2].get_num_vols() > max_fill
                or unassigned_groups[len(unassigned_groups) - 1].get_num_vols() + unassigned_groups[len(unassigned_groups) - 2].get_num_vols() + unassigned_groups[len(unassigned_groups) - 3].get_num_vols() < min_fill):
            # print(unassigned_jobsites[jobsite_index], "\n")
            jobsite_index -= 1
            continue
        # print(unassigned_jobsites[jobsite_index], "\n")
        # start from largest group
        group_index_1 = 0
        # if group is too large to even go under the max with the 2 smallest groups
        while group_index_1 < len(unassigned_groups) - 2 and unassigned_groups[group_index_1].get_num_vols() + unassigned_groups[len(unassigned_groups) - 1].get_num_vols() + unassigned_groups[len(unassigned_groups) - 2].get_num_vols() < min_fill:
            # print("\t", unassigned_groups[group_index_1], "\n")
            group_index_1 += 1
        # if group is out of range or is too small to be over the min
        if group_index_1 >= len(unassigned_groups) - 2 or unassigned_groups[group_index_1].get_num_vols() + unassigned_groups[group_index_1 + 1].get_num_vols() + unassigned_groups[group_index_1 + 2].get_num_vols() > max_fill:
            jobsite_index -= 1
            continue
        # go through each group
        while jobsite_index >= 0:
            # print("\t", unassigned_groups[group_index_1], "\n")
            group_index_2 = group_index_1 + 1
            # if second group is too large
            while group_index_2 < len(unassigned_groups) - 1 and unassigned_groups[group_index_1].get_num_vols() + unassigned_groups[group_index_2].get_num_vols() + unassigned_groups[len(unassigned_groups) - 1].get_num_vols() < min_fill:
                # print("\t\t", unassigned_groups[group_index_2], "\n")
                group_index_2 += 1
            # if second group is out of range or is too small
            if group_index_2 >= len(unassigned_groups) - 1 or unassigned_groups[group_index_1].get_num_vols() + unassigned_groups[group_index_2].get_num_vols() + unassigned_groups[group_index_2 + 1].get_num_vols() > max_fill:
                group_index_1 += 1
                if group_index_1 >= len(unassigned_groups) - 2:
                    jobsite_index -= 1
                    break
                continue
            # go through each second group
            while group_index_2 < len(unassigned_groups) - 1:
                # print("\t\t", unassigned_groups[group_index_2], "\n")
                group_index_3 = group_index_2 + 1
                # go through each third group assessing if small enough
                while group_index_3 < len(unassigned_groups) and unassigned_groups[group_index_1].get_num_vols() + unassigned_groups[group_index_2].get_num_vols() + unassigned_groups[group_index_3].get_num_vols() < min_fill:
                    # print("\t\t\t", unassigned_groups[group_index_3], "\n")
                    group_index_3 += 1
                # it's a match!
                if group_index_3 < len(unassigned_groups) and unassigned_groups[group_index_1].get_num_vols() + unassigned_groups[group_index_2].get_num_vols() + unassigned_groups[group_index_3].get_num_vols() <= max_fill:
                    # print("\t\t\t", unassigned_groups[group_index_3], "\n")
                    unassigned_jobsites[jobsite_index].add_group(unassigned_groups[group_index_1])
                    unassigned_jobsites[jobsite_index].add_group(unassigned_groups[group_index_2])
                    unassigned_jobsites[jobsite_index].add_group(unassigned_groups[group_index_3])
                    unassigned_groups[group_index_1].add_jobsite(unassigned_jobsites[jobsite_index])
                    unassigned_groups[group_index_2].add_jobsite(unassigned_jobsites[jobsite_index])
                    unassigned_groups[group_index_3].add_jobsite(unassigned_jobsites[jobsite_index])

                    assigned_jobsites.append(copy.deepcopy(unassigned_jobsites[jobsite_index]))
                    del unassigned_jobsites[jobsite_index]

                    assigned_groups.append(copy.deepcopy(unassigned_groups[group_index_1]))
                    assigned_groups.append(copy.deepcopy(unassigned_groups[group_index_2]))
                    assigned_groups.append(copy.deepcopy(unassigned_groups[group_index_3]))
                    del unassigned_groups[group_index_3] 
                    del unassigned_groups[group_index_2]
                    del unassigned_groups[group_index_1]  
                    flag = True
                    jobsite_index -= 1
                    break 
                # if not a match, move to next second jobsite
                group_index_2 += 1
                # if second group is not a viable index
                if group_index_2 > len(unassigned_groups) - 2:
                    group_index_1 += 1
                    # if first group is not a viable index
                    if group_index_1 > len(unassigned_groups) - 3:
                        jobsite_index -= 1
                        flag = True
                    break
            if flag:
                flag = False
                break
def match1to3_under(leniency):
    flag = False
    # start from biggest group
    group_index = 0
    while unassigned_groups[group_index].get_num_vols() < 45:
        group_index += 1
    while group_index < len(unassigned_groups) and len(unassigned_jobsites) >= 3:
        # calculate the minimum and maximum volunteers requested from jobsites that'll satisfy group
        min_fill = unassigned_groups[group_index].get_num_vols() / (FILL_PERCENT + leniency)
        max_fill = unassigned_groups[group_index].get_num_vols() / (FILL_PERCENT - leniency)
        # if we can tell this group will never be satisfied from the get-go because it is too small or big
        if (unassigned_jobsites[len(unassigned_jobsites) - 1].get_num_vols_requested() + unassigned_jobsites[len(unassigned_jobsites) - 1].get_num_vols_requested() + unassigned_jobsites[len(unassigned_jobsites) - 1].get_num_vols_requested() < min_fill
                or unassigned_jobsites[0].get_num_vols_requested() + unassigned_jobsites[1].get_num_vols_requested() + unassigned_jobsites[2].get_num_vols_requested() > max_fill):
            # print(unassigned_groups[group_index], "\n")
            group_index += 1
            continue
        # print(unassigned_groups[group_index], "\n")
        # start from smallest jobsite
        jobsite_index_1 = len(unassigned_jobsites) - 1
        while jobsite_index_1 >= 2 and unassigned_jobsites[jobsite_index_1].get_num_vols_requested() < 15:
            jobsite_index_1 -= 1
        # if jobsite is too small to even surpass max with the 2 biggest jobsites
        while jobsite_index_1 >= 2 and unassigned_jobsites[jobsite_index_1].get_num_vols_requested() + unassigned_jobsites[0].get_num_vols_requested() + unassigned_jobsites[1].get_num_vols_requested() > max_fill:
            # print("\t", unassigned_jobsites[jobsite_index_1], "\n")
            jobsite_index_1 -= 1
        # if jobsite is out of range or is too big to be under the minimum with the 2 smallest jobsites
        if jobsite_index_1 < 2 or unassigned_jobsites[jobsite_index_1].get_num_vols_requested() + unassigned_jobsites[jobsite_index_1 - 1].get_num_vols_requested() + unassigned_jobsites[jobsite_index_1 - 2].get_num_vols_requested() < min_fill:
            group_index += 1
            continue
        # go through each jobsite
        while jobsite_index_1 >= 2:
            # print("\t", unassigned_jobsites[jobsite_index_1], "\n")
            jobsite_index_2 = jobsite_index_1 - 1
            # if second jobsite is too small
            while jobsite_index_2 >= 1 and unassigned_jobsites[jobsite_index_1].get_num_vols_requested() + unassigned_jobsites[jobsite_index_2].get_num_vols_requested() + unassigned_jobsites[0].get_num_vols_requested() > max_fill:
                # print("\t\t", unassigned_jobsites[jobsite_index_2], "\n")
                jobsite_index_2 -= 1
            # if second jobsite is out of range or is too big
            if jobsite_index_2 < 1 or unassigned_jobsites[jobsite_index_1].get_num_vols_requested() + unassigned_jobsites[jobsite_index_2].get_num_vols_requested() + unassigned_jobsites[jobsite_index_2 - 1].get_num_vols_requested() < min_fill:
                jobsite_index_1 -= 1
                continue
            # go through each second jobsite
            while jobsite_index_2 >= 1:
                # print("\t\t", unassigned_jobsites[jobsite_index_2], "\n")
                jobsite_index_3 = jobsite_index_2 - 1
                # go through each third jobsite assessing if big enough
                while jobsite_index_3 >= 0 and unassigned_jobsites[jobsite_index_1].get_num_vols_requested() + unassigned_jobsites[jobsite_index_2].get_num_vols_requested() + unassigned_jobsites[jobsite_index_3].get_num_vols_requested() > max_fill:
                    # print("\t\t\t", unassigned_jobsites[jobsite_index_3], "\n")
                    jobsite_index_3 -= 1
                # if it's a match!
                if jobsite_index_3 >= 0 and unassigned_jobsites[jobsite_index_1].get_num_vols_requested() + unassigned_jobsites[jobsite_index_2].get_num_vols_requested() + unassigned_jobsites[jobsite_index_3].get_num_vols_requested() >= min_fill:
                    # print("\t\t\t", unassigned_jobsites[jobsite_index_3], "\n")
                    unassigned_jobsites[jobsite_index_1].add_group(unassigned_groups[group_index])
                    unassigned_jobsites[jobsite_index_2].add_group(unassigned_groups[group_index])
                    unassigned_jobsites[jobsite_index_3].add_group(unassigned_groups[group_index])
                    unassigned_groups[group_index].add_jobsite(unassigned_jobsites[jobsite_index_1])
                    unassigned_groups[group_index].add_jobsite(unassigned_jobsites[jobsite_index_2])
                    unassigned_groups[group_index].add_jobsite(unassigned_jobsites[jobsite_index_3])

                    assigned_jobsites.append(copy.deepcopy(unassigned_jobsites[jobsite_index_1]))
                    assigned_jobsites.append(copy.deepcopy(unassigned_jobsites[jobsite_index_2]))
                    assigned_jobsites.append(copy.deepcopy(unassigned_jobsites[jobsite_index_3]))
                    del unassigned_jobsites[jobsite_index_1]
                    del unassigned_jobsites[jobsite_index_2]
                    del unassigned_jobsites[jobsite_index_3]

                    assigned_groups.append(copy.deepcopy(unassigned_groups[group_index]))
                    del unassigned_groups[group_index]
                    flag = True
                    break
                # if not a match, move to next second jobsite 
                jobsite_index_2 -= 1
                # if second jobsite isn't viable index
                if jobsite_index_2 < 1:
                    jobsite_index_1 -= 1
                    # if first jobsite isn't a viable index
                    if jobsite_index_1 < 2:
                        group_index += 1
                        flag = True
                    break
            if flag:
                flag = False
                break

# matching is done walking both lists forward
def match1to1_forward(leniency):
    jobsite_index = 0
    group_index = 0
    while jobsite_index < len(unassigned_jobsites):
        # print(unassigned_jobsites[jobsite_index], "\n")
        min_fill = unassigned_jobsites[jobsite_index].get_num_vols_requested() * (FILL_PERCENT - leniency)
        max_fill = unassigned_jobsites[jobsite_index].get_num_vols_requested() * (FILL_PERCENT + leniency)
        while  group_index < len(unassigned_groups) and unassigned_groups[group_index].get_num_vols() < min_fill:
            # print("\t", unassigned_groups[group_index], "\n")
            group_index += 1
        if group_index < len(unassigned_groups) and unassigned_groups[group_index].get_num_vols() < max_fill:
            # print("\t", unassigned_groups[group_index], "\n")
            unassigned_jobsites[jobsite_index].add_group(unassigned_groups[group_index])
            unassigned_groups[group_index].add_jobsite(unassigned_jobsites[jobsite_index])

            assigned_jobsites.append(copy.deepcopy(unassigned_jobsites[jobsite_index]))
            del unassigned_jobsites[jobsite_index]

            assigned_groups.append(copy.deepcopy(unassigned_groups[group_index]))
            del unassigned_groups[group_index]
        else:
            jobsite_index += 1
def match2to1_forward(leniency):
    jobsite_index = 0
    while jobsite_index < len(unassigned_jobsites) and len(unassigned_groups) >= 2:
        min_fill = unassigned_jobsites[jobsite_index].get_num_vols_requested() * (FILL_PERCENT - leniency) 
        max_fill = unassigned_jobsites[jobsite_index].get_num_vols_requested() * (FILL_PERCENT + leniency) 
        # if we can tell this jobsite will never be satisfied from the get-go because it is too small or big
        if unassigned_groups[0].get_num_vols() + unassigned_groups[1].get_num_vols() > max_fill:
            # print(unassigned_jobsites[jobsite_index], "\n")
            jobsite_index += 1
            continue
        if unassigned_groups[len(unassigned_groups) - 1].get_num_vols() + unassigned_groups[len(unassigned_groups) - 2].get_num_vols() < min_fill:
            break
        # print(unassigned_jobsites[jobsite_index], "\n")
        group_index_1 = 0
        # if group is too large to even go under the max with the smallest group
        while group_index_1 < len(unassigned_groups) and unassigned_groups[group_index_1].get_num_vols() + unassigned_groups[len(unassigned_groups) - 1].get_num_vols() < min_fill:
            # print("\t", unassigned_groups[group_index_1], "\n")
            group_index_1 += 1
        # if group is out of range or is too small to be over the min
        if group_index_1 >= len(unassigned_groups) or unassigned_groups[group_index_1].get_num_vols() + unassigned_groups[group_index_1 + 1].get_num_vols() > max_fill:
            jobsite_index += 1
            continue
        while True:
            # print("\t", unassigned_groups[group_index_1], "\n")
            group_index_2 = group_index_1 + 1
            while group_index_2 < len(unassigned_groups) and unassigned_groups[group_index_1].get_num_vols() + unassigned_groups[group_index_2].get_num_vols() < min_fill:
                # print("\t\t", unassigned_groups[group_index_2], "\n")
                group_index_2 += 1
            if group_index_2 < len(unassigned_groups) and unassigned_groups[group_index_1].get_num_vols() + unassigned_groups[group_index_2].get_num_vols() <= max_fill:
                # print("\t\t", unassigned_groups[group_index_2], "\n")
                unassigned_jobsites[jobsite_index].add_group(unassigned_groups[group_index_1])
                unassigned_jobsites[jobsite_index].add_group(unassigned_groups[group_index_2])
                unassigned_groups[group_index_1].add_jobsite(unassigned_jobsites[jobsite_index])
                unassigned_groups[group_index_2].add_jobsite(unassigned_jobsites[jobsite_index])

                assigned_jobsites.append(copy.deepcopy(unassigned_jobsites[jobsite_index]))
                del unassigned_jobsites[jobsite_index]

                assigned_groups.append(copy.deepcopy(unassigned_groups[group_index_1]))
                assigned_groups.append(copy.deepcopy(unassigned_groups[group_index_2]))
                del unassigned_groups[group_index_2]
                del unassigned_groups[group_index_1]
                break
            elif group_index_2 < len(unassigned_groups) and group_index_2 == group_index_1 + 1:
                jobsite_index += 1
                break
            group_index_1 += 1
            if group_index_1 >= len(unassigned_groups) - 1:
                jobsite_index += 1
                break
def match1to2_forward(leniency):
    group_index = 0
    while unassigned_groups[group_index].get_num_vols() < 30:
        group_index += 1
    while group_index < len(unassigned_groups) and len(unassigned_jobsites) >= 2:
        min_fill = unassigned_groups[group_index].get_num_vols() / (FILL_PERCENT + leniency)
        max_fill = unassigned_groups[group_index].get_num_vols() / (FILL_PERCENT - leniency)
        # if we can tell this group will never be satisfied from the get-go because it is too small or big
        if unassigned_jobsites[len(unassigned_jobsites) - 1].get_num_vols_requested() + unassigned_jobsites[len(unassigned_jobsites) - 2].get_num_vols_requested() < min_fill:
            # print(unassigned_groups[group_index], "\n")
            group_index += 1
            continue
        if unassigned_jobsites[0].get_num_vols_requested() + unassigned_jobsites[1].get_num_vols_requested() > max_fill:
            break
        # print(unassigned_groups[group_index], "\n")
        # start from smallest jobsite
        jobsite_index_1 = 0
        while jobsite_index_1 < len(unassigned_jobsites) - 2 and unassigned_jobsites[jobsite_index_1].get_num_vols_requested() < 15:
            jobsite_index_1 += 1
            continue
        # if jobsite is too small to even surpass max with the biggest jobsite
        while jobsite_index_1 < len(unassigned_jobsites) - 2 and unassigned_jobsites[jobsite_index_1].get_num_vols_requested() + unassigned_jobsites[len(unassigned_jobsites) - 1].get_num_vols_requested() < min_fill:
            # print("\t", unassigned_jobsites[jobsite_index_1], "\n")
            jobsite_index_1 += 1
        # if jobsite is out of range or is too big to be under the minimum with the smallest jobsite
        if jobsite_index_1 >= len(unassigned_jobsites) - 2 or unassigned_jobsites[jobsite_index_1].get_num_vols_requested() + unassigned_jobsites[jobsite_index_1 + 1].get_num_vols_requested() > max_fill:
            group_index += 1
            continue
        while True:
            # print("\t", unassigned_jobsites[jobsite_index_1], "\n")
            jobsite_index_2 = jobsite_index_1 + 1
            while jobsite_index_2 < len(unassigned_jobsites) and unassigned_jobsites[jobsite_index_1].get_num_vols_requested() + unassigned_jobsites[jobsite_index_2].get_num_vols_requested() < min_fill:
                # print("\t\t", unassigned_jobsites[jobsite_index_2], "\n")
                jobsite_index_2 += 1
            if jobsite_index_2 < len(unassigned_jobsites) and unassigned_jobsites[jobsite_index_1].get_num_vols_requested() + unassigned_jobsites[jobsite_index_2].get_num_vols_requested() <= max_fill:
                # print("\t\t", unassigned_jobsites[jobsite_index_2], "\n")
                unassigned_jobsites[jobsite_index_1].add_group(unassigned_groups[group_index])
                unassigned_jobsites[jobsite_index_2].add_group(unassigned_groups[group_index])
                unassigned_groups[group_index].add_jobsite(unassigned_jobsites[jobsite_index_1])
                unassigned_groups[group_index].add_jobsite(unassigned_jobsites[jobsite_index_2])

                assigned_jobsites.append(copy.deepcopy(unassigned_jobsites[jobsite_index_1]))
                assigned_jobsites.append(copy.deepcopy(unassigned_jobsites[jobsite_index_2]))
                del unassigned_jobsites[jobsite_index_2]
                del unassigned_jobsites[jobsite_index_1]

                assigned_groups.append(copy.deepcopy(unassigned_groups[group_index]))
                del unassigned_groups[group_index]
                break
            elif jobsite_index_2 < len(unassigned_jobsites) and jobsite_index_2 == jobsite_index_1 + 1:
                group_index += 1
                break
            jobsite_index_1 += 1
            if jobsite_index_1 >= len(unassigned_groups) - 1:
                group_index += 1
                break
def match3to1_forward(leniency):
    flag = False
    jobsite_index = 0
    while jobsite_index < len(unassigned_jobsites) and len(unassigned_groups) >= 3:
        min_fill = unassigned_jobsites[jobsite_index].get_num_vols_requested() * (FILL_PERCENT - leniency) 
        max_fill = unassigned_jobsites[jobsite_index].get_num_vols_requested() * (FILL_PERCENT + leniency) 
        # if we can tell this jobsite will never be satisfied from the get-go because it is too big or small
        if unassigned_groups[0].get_num_vols() + unassigned_groups[1].get_num_vols() + unassigned_groups[2].get_num_vols() > max_fill:
            # print(unassigned_jobsites[jobsite_index], "\n")
            jobsite_index += 1
            continue
        if unassigned_groups[len(unassigned_groups) - 1].get_num_vols() + unassigned_groups[len(unassigned_groups) - 2].get_num_vols() + unassigned_groups[len(unassigned_groups) - 3].get_num_vols() < min_fill:
            break
        # print(unassigned_jobsites[jobsite_index], "\n")
        # start from largest group
        group_index_1 = 0
        # if group is too large to even go under the max with the 2 smallest groups
        while group_index_1 < len(unassigned_groups) - 2 and unassigned_groups[group_index_1].get_num_vols() + unassigned_groups[len(unassigned_groups) - 1].get_num_vols() + unassigned_groups[len(unassigned_groups) - 2].get_num_vols() < min_fill:
            # print("\t", unassigned_groups[group_index_1], "\n")
            group_index_1 += 1
        # if group is out of range or is too small to be over the min
        if group_index_1 >= len(unassigned_groups) - 2 or unassigned_groups[group_index_1].get_num_vols() + unassigned_groups[group_index_1 + 1].get_num_vols() + unassigned_groups[group_index_1 + 2].get_num_vols() > max_fill:
            jobsite_index -= 1
            continue
        while group_index_1 < len(unassigned_groups) and jobsite_index < len(unassigned_jobsites) and len(unassigned_groups) > 2:
            # print("\t", unassigned_groups[group_index_1], "\n")
            group_index_2 = group_index_1 + 1
            # if second group is too large
            while group_index_2 < len(unassigned_groups) - 1 and unassigned_groups[group_index_1].get_num_vols() + unassigned_groups[group_index_2].get_num_vols() + unassigned_groups[len(unassigned_groups) - 1].get_num_vols() < min_fill:
                # print("\t\t", unassigned_groups[group_index_2], "\n")
                group_index_2 += 1
            # if second group is out of range or is too small
            if group_index_2 >= len(unassigned_groups) - 1 or unassigned_groups[group_index_1].get_num_vols() + unassigned_groups[group_index_2].get_num_vols() + unassigned_groups[group_index_2 + 1].get_num_vols() > max_fill:
                group_index_1 += 1
                if group_index_1 >= len(unassigned_groups) - 2:
                    jobsite_index += 1
                    break
                continue
            while group_index_2 < len(unassigned_groups) and group_index_1 < len(unassigned_groups):
                # print("\t\t", unassigned_groups[group_index_2], "\n")
                group_index_3 = group_index_2 + 1
                while group_index_3 < len(unassigned_groups) and unassigned_groups[group_index_1].get_num_vols() + unassigned_groups[group_index_2].get_num_vols() + unassigned_groups[group_index_3].get_num_vols() < min_fill:
                    # print("\t\t\t", unassigned_groups[group_index_3], "\n")
                    group_index_3 += 1
                if group_index_3 < len(unassigned_groups) and unassigned_groups[group_index_1].get_num_vols() + unassigned_groups[group_index_2].get_num_vols() + unassigned_groups[group_index_3].get_num_vols() <= max_fill:
                    # print("\t\t\t", unassigned_groups[group_index_3], "\n")
                    unassigned_jobsites[jobsite_index].add_group(unassigned_groups[group_index_1])
                    unassigned_jobsites[jobsite_index].add_group(unassigned_groups[group_index_2])
                    unassigned_jobsites[jobsite_index].add_group(unassigned_groups[group_index_3])
                    unassigned_groups[group_index_1].add_jobsite(unassigned_jobsites[jobsite_index])
                    unassigned_groups[group_index_2].add_jobsite(unassigned_jobsites[jobsite_index])
                    unassigned_groups[group_index_3].add_jobsite(unassigned_jobsites[jobsite_index])

                    assigned_jobsites.append(copy.deepcopy(unassigned_jobsites[jobsite_index]))
                    del unassigned_jobsites[jobsite_index]

                    assigned_groups.append(copy.deepcopy(unassigned_groups[group_index_1]))
                    assigned_groups.append(copy.deepcopy(unassigned_groups[group_index_2]))
                    assigned_groups.append(copy.deepcopy(unassigned_groups[group_index_3]))
                    del unassigned_groups[group_index_3] 
                    del unassigned_groups[group_index_2]
                    del unassigned_groups[group_index_1]   
                    flag = True
                    break
                elif group_index_3 < len(unassigned_groups) and group_index_3 == group_index_2 + 1:
                        if group_index_2 == group_index_1 + 1:
                            jobsite_index += 1
                            flag = True
                            break
                        group_index_1 += 1
                        if group_index_1 > len(unassigned_groups):
                            jobsite_index += 1
                            flag = True
                        break
                group_index_2 += 1
                if group_index_2 >= len(unassigned_groups) - 1:
                    group_index_1 += 1
                    if group_index_1 > len(unassigned_groups) - 2:
                            jobsite_index += 1
                            flag = True
                    break
            if flag:
                flag = False
                break 
def match1to3_forward(leniency):
    flag = False
    group_index = 0
    while group_index < len(unassigned_groups) and unassigned_groups[group_index].get_num_vols() <= 45:
        group_index += 1
    while group_index < len(unassigned_groups) and len(unassigned_jobsites) >= 3:
        min_fill = unassigned_groups[group_index].get_num_vols() / (FILL_PERCENT + leniency)
        max_fill = unassigned_groups[group_index].get_num_vols() / (FILL_PERCENT - leniency)
        # if we can tell this group will never be satisfied from the get-go because it is too small or big
        if unassigned_jobsites[len(unassigned_jobsites) - 1].get_num_vols_requested() + unassigned_jobsites[len(unassigned_jobsites) - 1].get_num_vols_requested() + unassigned_jobsites[len(unassigned_jobsites) - 1].get_num_vols_requested() < min_fill:
            # print(unassigned_groups[group_index], "\n")
            group_index += 1
            continue
        if unassigned_jobsites[0].get_num_vols_requested() + unassigned_jobsites[1].get_num_vols_requested() + unassigned_jobsites[2].get_num_vols_requested() > max_fill:
            break
        # print(unassigned_groups[group_index], "\n")
        # start from smallest jobsite
        jobsite_index_1 = 0
        while jobsite_index_1 < len(unassigned_jobsites) - 2 and unassigned_jobsites[jobsite_index_1].get_num_vols_requested() < 15:
            jobsite_index_1 += 1
        # if jobsite is too small to even surpass max with the 2 biggest jobsites
        while jobsite_index_1 < len(unassigned_jobsites) - 2 and unassigned_jobsites[jobsite_index_1].get_num_vols_requested() + unassigned_jobsites[len(unassigned_jobsites) - 1].get_num_vols_requested() + unassigned_jobsites[len(unassigned_jobsites) - 2].get_num_vols_requested() < min_fill:
            # print("\t", unassigned_jobsites[jobsite_index_1], "\n")
            jobsite_index_1 += 1
        # if jobsite is out of range or is too big to be under the minimum with the 2 smallest jobsites
        if jobsite_index_1 >= len(unassigned_jobsites) - 2 or unassigned_jobsites[jobsite_index_1].get_num_vols_requested() + unassigned_jobsites[jobsite_index_1 + 1].get_num_vols_requested() + unassigned_jobsites[jobsite_index_1 + 2].get_num_vols_requested() > max_fill:
            group_index += 1
            continue
        while jobsite_index_1 < len(unassigned_jobsites):
            # print("\t", unassigned_jobsites[jobsite_index_1], "\n")
            jobsite_index_2 = jobsite_index_1 + 1
            # if second jobsite is too small
            while jobsite_index_2 < len(unassigned_jobsites) - 1 and unassigned_jobsites[jobsite_index_1].get_num_vols_requested() + unassigned_jobsites[jobsite_index_2].get_num_vols_requested() + unassigned_jobsites[len(unassigned_jobsites) - 1].get_num_vols_requested() < min_fill:
                # print("\t\t", unassigned_jobsites[jobsite_index_2], "\n")
                jobsite_index_2 += 1
            # if second jobsite is out of range or is too big
            if jobsite_index_2 >= len(unassigned_jobsites) - 1 or unassigned_jobsites[jobsite_index_1].get_num_vols_requested() + unassigned_jobsites[jobsite_index_2].get_num_vols_requested() + unassigned_jobsites[jobsite_index_2 + 1].get_num_vols_requested() > max_fill:
                jobsite_index_1 += 1
                continue
            while jobsite_index_2 < len(unassigned_jobsites) and jobsite_index_1 < len(unassigned_jobsites) and group_index < len(unassigned_groups) and len(unassigned_jobsites) > 2:
                # print("\t\t", unassigned_jobsites[jobsite_index_2], "\n")
                jobsite_index_3 = jobsite_index_2 + 1
                while jobsite_index_3 < len(unassigned_jobsites) and unassigned_jobsites[jobsite_index_1].get_num_vols_requested() + unassigned_jobsites[jobsite_index_2].get_num_vols_requested() + unassigned_jobsites[jobsite_index_3].get_num_vols_requested() < min_fill:
                    # print("\t\t\t", unassigned_jobsites[jobsite_index_3], "\n")
                    jobsite_index_3 += 1
                if jobsite_index_3 < len(unassigned_jobsites) and unassigned_jobsites[jobsite_index_1].get_num_vols_requested() + unassigned_jobsites[jobsite_index_2].get_num_vols_requested() + unassigned_jobsites[jobsite_index_3].get_num_vols_requested() <= max_fill:
                    # print("\t\t\t", unassigned_jobsites[jobsite_index_3], "\n")
                    unassigned_jobsites[jobsite_index_1].add_group(unassigned_groups[group_index])
                    unassigned_jobsites[jobsite_index_2].add_group(unassigned_groups[group_index])
                    unassigned_jobsites[jobsite_index_3].add_group(unassigned_groups[group_index])
                    unassigned_groups[group_index].add_jobsite(unassigned_jobsites[jobsite_index_1])
                    unassigned_groups[group_index].add_jobsite(unassigned_jobsites[jobsite_index_2])
                    unassigned_groups[group_index].add_jobsite(unassigned_jobsites[jobsite_index_3])

                    assigned_jobsites.append(copy.deepcopy(unassigned_jobsites[jobsite_index_1]))
                    assigned_jobsites.append(copy.deepcopy(unassigned_jobsites[jobsite_index_2]))
                    assigned_jobsites.append(copy.deepcopy(unassigned_jobsites[jobsite_index_3]))
                    del unassigned_jobsites[jobsite_index_3]
                    del unassigned_jobsites[jobsite_index_2]
                    del unassigned_jobsites[jobsite_index_1]

                    assigned_groups.append(copy.deepcopy(unassigned_groups[group_index]))
                    del unassigned_groups[group_index]
                    flag = True
                    break
                elif jobsite_index_3 < len(unassigned_jobsites) and jobsite_index_3 == jobsite_index_2 + 1:
                        if jobsite_index_2 == jobsite_index_1 + 1:
                            group_index += 1
                            flag = True
                            break
                        jobsite_index_1 += 1
                        if jobsite_index_1 > len(unassigned_jobsites):
                            group_index += 1
                            flag = True
                        break
                jobsite_index_2 += 1
                if jobsite_index_2 >= len(unassigned_jobsites) - 1:
                    jobsite_index_1 += 1
                    if jobsite_index_1 > len(unassigned_jobsites) - 2:
                            group_index += 1
                            flag = True
                    break
            if flag:
                flag = False
                break 
# matching is done walking both lists backward
def match1to1_backward(leniency):
    unassigned_jobsites.reverse()
    unassigned_groups.reverse()

    jobsite_index = 0
    group_index = 0
    while jobsite_index < len(unassigned_jobsites):
        # print(unassigned_jobsites[jobsite_index], "\n")
        min_fill = unassigned_jobsites[jobsite_index].get_num_vols_requested() * (FILL_PERCENT - leniency)
        max_fill = unassigned_jobsites[jobsite_index].get_num_vols_requested() * (FILL_PERCENT + leniency)
        while  group_index < len(unassigned_groups) and unassigned_groups[group_index].get_num_vols() > max_fill:
            # print("\t", unassigned_groups[group_index], "\n")
            group_index += 1
        if group_index < len(unassigned_groups) and unassigned_groups[group_index].get_num_vols() > min_fill:
            # print("\t", unassigned_groups[group_index], "\n")
            unassigned_jobsites[jobsite_index].add_group(unassigned_groups[group_index])
            unassigned_groups[group_index].add_jobsite(unassigned_jobsites[jobsite_index])

            assigned_jobsites.append(copy.deepcopy(unassigned_jobsites[jobsite_index]))
            del unassigned_jobsites[jobsite_index]

            assigned_groups.append(copy.deepcopy(unassigned_groups[group_index]))
            del unassigned_groups[group_index]
        else:
            jobsite_index += 1
    
    unassigned_groups.sort()
    unassigned_jobsites.sort()
def match2to1_backward(leniency):
    unassigned_jobsites.reverse()
    unassigned_groups.reverse()

    jobsite_index = 0
    while jobsite_index < len(unassigned_jobsites) and len(unassigned_groups) >= 2:
        min_fill = unassigned_jobsites[jobsite_index].get_num_vols_requested() * (FILL_PERCENT - leniency) 
        max_fill = unassigned_jobsites[jobsite_index].get_num_vols_requested() * (FILL_PERCENT + leniency) 
        # if we can tell this jobsite will never be satisfied from the get-go because it is too small or big
        if unassigned_groups[0].get_num_vols() + unassigned_groups[1].get_num_vols() < min_fill:
            # print(unassigned_jobsites[jobsite_index], "\n")
            jobsite_index += 1
            continue
        if unassigned_groups[len(unassigned_groups) - 1].get_num_vols() + unassigned_groups[len(unassigned_groups) - 2].get_num_vols() > max_fill:
            break
        # print(unassigned_jobsites[jobsite_index], "\n")
        group_index_1 = 0
        # if group is too large to even go under the max with the smallest group
        while group_index_1 < len(unassigned_groups) and unassigned_groups[group_index_1].get_num_vols() + unassigned_groups[len(unassigned_groups) - 1].get_num_vols() > max_fill:
            # print("\t", unassigned_groups[group_index_1], "\n")
            group_index_1 += 1
        # if group is out of range or is too small to be over the min
        if group_index_1 >= len(unassigned_groups) or unassigned_groups[group_index_1].get_num_vols() + unassigned_groups[group_index_1 + 1].get_num_vols() < min_fill:
            jobsite_index += 1
            continue
        while True:
            # print("\t", unassigned_groups[group_index_1], "\n")
            group_index_2 = group_index_1 + 1
            while group_index_2 < len(unassigned_groups) and unassigned_groups[group_index_1].get_num_vols() + unassigned_groups[group_index_2].get_num_vols() > max_fill:
                # print("\t\t", unassigned_groups[group_index_2], "\n")
                group_index_2 += 1
            if group_index_2 < len(unassigned_groups) and unassigned_groups[group_index_1].get_num_vols() + unassigned_groups[group_index_2].get_num_vols() >= min_fill:
                # print("\t\t", unassigned_groups[group_index_2], "\n")
                unassigned_jobsites[jobsite_index].add_group(unassigned_groups[group_index_1])
                unassigned_jobsites[jobsite_index].add_group(unassigned_groups[group_index_2])
                unassigned_groups[group_index_1].add_jobsite(unassigned_jobsites[jobsite_index])
                unassigned_groups[group_index_2].add_jobsite(unassigned_jobsites[jobsite_index])

                assigned_jobsites.append(copy.deepcopy(unassigned_jobsites[jobsite_index]))
                del unassigned_jobsites[jobsite_index]

                assigned_groups.append(copy.deepcopy(unassigned_groups[group_index_1]))
                assigned_groups.append(copy.deepcopy(unassigned_groups[group_index_2]))
                del unassigned_groups[group_index_2]
                del unassigned_groups[group_index_1]
                break
            elif group_index_2 < len(unassigned_groups) and group_index_2 == group_index_1 + 1:
                jobsite_index += 1
                break
            group_index_1 += 1
            if group_index_1 >= len(unassigned_groups) - 1:
                jobsite_index += 1
                break
    unassigned_groups.sort()
    unassigned_jobsites.sort()
def match1to2_backward(leniency):
    unassigned_jobsites.reverse()
    unassigned_groups.reverse()

    group_index = 0
    while group_index < len(unassigned_groups) and len(unassigned_jobsites) >= 2 and unassigned_groups[group_index].get_num_vols() >= 30:
        min_fill = unassigned_groups[group_index].get_num_vols() / (FILL_PERCENT + leniency)
        max_fill = unassigned_groups[group_index].get_num_vols() / (FILL_PERCENT - leniency)
        # if we can tell this group will never be satisfied from the get-go because it is too small or big
        if unassigned_jobsites[0].get_num_vols_requested() + unassigned_jobsites[1].get_num_vols_requested() < min_fill:
            # print(unassigned_groups[group_index], "\n")
            group_index += 1
            continue
        if unassigned_jobsites[len(unassigned_jobsites) - 1].get_num_vols_requested() + unassigned_jobsites[len(unassigned_jobsites) - 2].get_num_vols_requested() > max_fill:
            break
        # print(unassigned_groups[group_index], "\n")
        # start from smallest jobsite
        jobsite_index_1 = 0
        while jobsite_index_1 < len(unassigned_jobsites) - 2 and unassigned_jobsites[jobsite_index_1].get_num_vols_requested() < 15:
            jobsite_index_1 += 1
            continue
        # if jobsite is too small to even surpass max with the biggest jobsite
        while jobsite_index_1 < len(unassigned_jobsites) - 2 and unassigned_jobsites[jobsite_index_1].get_num_vols_requested() + unassigned_jobsites[len(unassigned_jobsites) - 1].get_num_vols_requested() > max_fill:
            # print("\t", unassigned_jobsites[jobsite_index_1], "\n")
            jobsite_index_1 += 1
        # if jobsite is out of range or is too big to be under the minimum with the smallest jobsite
        if jobsite_index_1 >= len(unassigned_jobsites) - 2 or unassigned_jobsites[jobsite_index_1].get_num_vols_requested() + unassigned_jobsites[jobsite_index_1 + 1].get_num_vols_requested() < min_fill:
            group_index += 1
            continue
        while True:
            # print("\t", unassigned_jobsites[jobsite_index_1], "\n")
            jobsite_index_2 = jobsite_index_1 + 1
            while jobsite_index_2 < len(unassigned_jobsites) and unassigned_jobsites[jobsite_index_1].get_num_vols_requested() + unassigned_jobsites[jobsite_index_2].get_num_vols_requested() > max_fill:
                # print("\t\t", unassigned_jobsites[jobsite_index_2], "\n")
                jobsite_index_2 += 1
            if jobsite_index_2 < len(unassigned_jobsites) and unassigned_jobsites[jobsite_index_1].get_num_vols_requested() + unassigned_jobsites[jobsite_index_2].get_num_vols_requested() >= min_fill:
                # print("\t\t", unassigned_jobsites[jobsite_index_2], "\n")
                unassigned_jobsites[jobsite_index_1].add_group(unassigned_groups[group_index])
                unassigned_jobsites[jobsite_index_2].add_group(unassigned_groups[group_index])
                unassigned_groups[group_index].add_jobsite(unassigned_jobsites[jobsite_index_1])
                unassigned_groups[group_index].add_jobsite(unassigned_jobsites[jobsite_index_2])

                assigned_jobsites.append(copy.deepcopy(unassigned_jobsites[jobsite_index_1]))
                assigned_jobsites.append(copy.deepcopy(unassigned_jobsites[jobsite_index_2]))
                del unassigned_jobsites[jobsite_index_2]
                del unassigned_jobsites[jobsite_index_1]

                assigned_groups.append(copy.deepcopy(unassigned_groups[group_index]))
                del unassigned_groups[group_index]
                break
            elif jobsite_index_2 < len(unassigned_jobsites) and jobsite_index_2 == jobsite_index_1 + 1:
                group_index += 1
                break
            jobsite_index_1 += 1
            if jobsite_index_1 >= len(unassigned_groups) - 1:
                group_index += 1
                break
    unassigned_jobsites.sort()
    unassigned_groups.sort()
def match3to1_backward(leniency):
    unassigned_jobsites.reverse()
    unassigned_groups.reverse()

    flag = False
    jobsite_index = 0
    while jobsite_index < len(unassigned_jobsites) and len(unassigned_groups) >= 3:
        min_fill = unassigned_jobsites[jobsite_index].get_num_vols_requested() * (FILL_PERCENT - leniency) 
        max_fill = unassigned_jobsites[jobsite_index].get_num_vols_requested() * (FILL_PERCENT + leniency) 
        # if we can tell this jobsite will never be satisfied from the get-go because it is too big or small
        if unassigned_groups[0].get_num_vols() + unassigned_groups[1].get_num_vols() + unassigned_groups[2].get_num_vols() < min_fill:
            # print(unassigned_jobsites[jobsite_index], "\n")
            jobsite_index += 1
            continue
        # print(unassigned_jobsites[jobsite_index], "\n")
        if unassigned_groups[len(unassigned_groups) - 1].get_num_vols() + unassigned_groups[len(unassigned_groups) - 2].get_num_vols() + unassigned_groups[len(unassigned_groups) - 3].get_num_vols() > max_fill:
            break
        # start from largest group
        group_index_1 = 0
        # if group is too large to even go under the max with the 2 smallest groups
        while group_index_1 < len(unassigned_groups) - 2 and unassigned_groups[group_index_1].get_num_vols() + unassigned_groups[len(unassigned_groups) - 1].get_num_vols() + unassigned_groups[len(unassigned_groups) - 2].get_num_vols() > max_fill:
            # print("\t", unassigned_groups[group_index_1], "\n")
            group_index_1 += 1
        # if group is out of range or is too small to be over the min
        if group_index_1 >= len(unassigned_groups) - 2 or unassigned_groups[group_index_1].get_num_vols() + unassigned_groups[group_index_1 + 1].get_num_vols() + unassigned_groups[group_index_1 + 2].get_num_vols() < min_fill:
            jobsite_index += 1
            continue
        while group_index_1 < len(unassigned_groups) and jobsite_index < len(unassigned_jobsites) and len(unassigned_groups) > 2:
            # print("\t", unassigned_groups[group_index_1], "\n")
            group_index_2 = group_index_1 + 1
            # if second group is too large
            while group_index_2 < len(unassigned_groups) - 1 and unassigned_groups[group_index_1].get_num_vols() + unassigned_groups[group_index_2].get_num_vols() + unassigned_groups[len(unassigned_groups) - 1].get_num_vols() > max_fill:
                # print("\t\t", unassigned_groups[group_index_2], "\n")
                group_index_2 += 1
            # if second group is out of range or is too small
            if group_index_2 >= len(unassigned_groups) - 1 or unassigned_groups[group_index_1].get_num_vols() + unassigned_groups[group_index_2].get_num_vols() + unassigned_groups[group_index_2 + 1].get_num_vols() < min_fill:
                group_index_1 += 1
                if group_index_1 >= len(unassigned_groups) - 2:
                    jobsite_index += 1
                    break
                continue
            while group_index_2 < len(unassigned_groups) and group_index_1 < len(unassigned_groups):
                # print("\t\t", unassigned_groups[group_index_2], "\n")
                group_index_3 = group_index_2 + 1
                while group_index_3 < len(unassigned_groups) and unassigned_groups[group_index_1].get_num_vols() + unassigned_groups[group_index_2].get_num_vols() + unassigned_groups[group_index_3].get_num_vols() > max_fill:
                    # print("\t\t\t", unassigned_groups[group_index_3], "\n")
                    group_index_3 += 1
                if group_index_3 < len(unassigned_groups) and unassigned_groups[group_index_1].get_num_vols() + unassigned_groups[group_index_2].get_num_vols() + unassigned_groups[group_index_3].get_num_vols() >= min_fill:
                    # print("\t\t\t", unassigned_groups[group_index_3], "\n")
                    unassigned_jobsites[jobsite_index].add_group(unassigned_groups[group_index_1])
                    unassigned_jobsites[jobsite_index].add_group(unassigned_groups[group_index_2])
                    unassigned_jobsites[jobsite_index].add_group(unassigned_groups[group_index_3])
                    unassigned_groups[group_index_1].add_jobsite(unassigned_jobsites[jobsite_index])
                    unassigned_groups[group_index_2].add_jobsite(unassigned_jobsites[jobsite_index])
                    unassigned_groups[group_index_3].add_jobsite(unassigned_jobsites[jobsite_index])

                    assigned_jobsites.append(copy.deepcopy(unassigned_jobsites[jobsite_index]))
                    del unassigned_jobsites[jobsite_index]

                    assigned_groups.append(copy.deepcopy(unassigned_groups[group_index_1]))
                    assigned_groups.append(copy.deepcopy(unassigned_groups[group_index_2]))
                    assigned_groups.append(copy.deepcopy(unassigned_groups[group_index_3]))
                    del unassigned_groups[group_index_3] 
                    del unassigned_groups[group_index_2]
                    del unassigned_groups[group_index_1]   
                    flag = True
                    break
                elif group_index_3 < len(unassigned_groups) and group_index_3 == group_index_2 + 1:
                        if group_index_2 == group_index_1 + 1:
                            jobsite_index += 1
                            flag = True
                            break
                        group_index_1 += 1
                        if group_index_1 > len(unassigned_groups):
                            jobsite_index += 1
                            flag = True
                        break
                group_index_2 += 1
                if group_index_2 >= len(unassigned_groups) - 1:
                    group_index_1 += 1
                    if group_index_1 > len(unassigned_groups) - 2:
                            jobsite_index += 1
                            flag = True
                    break
            if flag:
                flag = False
                break 
    unassigned_jobsites.sort()
    unassigned_groups.sort()
def match1to3_backward(leniency):
    unassigned_jobsites.reverse()
    unassigned_groups.reverse()

    flag = False
    group_index = 0
    while group_index < len(unassigned_groups) and len(unassigned_jobsites) >= 3 and unassigned_groups[group_index].get_num_vols() >= 45:
        min_fill = unassigned_groups[group_index].get_num_vols() / (FILL_PERCENT + leniency)
        max_fill = unassigned_groups[group_index].get_num_vols() / (FILL_PERCENT - leniency)
        # if we can tell this group will never be satisfied from the get-go because it is too small or big
        if unassigned_jobsites[len(unassigned_jobsites) - 1].get_num_vols_requested() + unassigned_jobsites[len(unassigned_jobsites) - 1].get_num_vols_requested() + unassigned_jobsites[len(unassigned_jobsites) - 1].get_num_vols_requested() > max_fill:
            # print(unassigned_groups[group_index], "\n")
            group_index += 1
            continue
        if unassigned_jobsites[0].get_num_vols_requested() + unassigned_jobsites[1].get_num_vols_requested() + unassigned_jobsites[2].get_num_vols_requested() < min_fill:
            break
        # print(unassigned_groups[group_index], "\n")
        # start from smallest jobsite
        jobsite_index_1 = 0
        while jobsite_index_1 < len(unassigned_jobsites) - 2 and unassigned_jobsites[jobsite_index_1].get_num_vols_requested() < 15:
            jobsite_index_1 += 1
        # if jobsite is too small to even surpass max with the 2 biggest jobsites
        while jobsite_index_1 < len(unassigned_jobsites) - 2 and unassigned_jobsites[jobsite_index_1].get_num_vols_requested() + unassigned_jobsites[len(unassigned_jobsites) - 1].get_num_vols_requested() + unassigned_jobsites[len(unassigned_jobsites) - 2].get_num_vols_requested() > max_fill:
            # print("\t", unassigned_jobsites[jobsite_index_1], "\n")
            jobsite_index_1 += 1
        # if jobsite is out of range or is too big to be under the minimum with the 2 smallest jobsites
        if jobsite_index_1 >= len(unassigned_jobsites) - 2 or unassigned_jobsites[jobsite_index_1].get_num_vols_requested() + unassigned_jobsites[jobsite_index_1 + 1].get_num_vols_requested() + unassigned_jobsites[jobsite_index_1 + 2].get_num_vols_requested() < min_fill:
            group_index += 1
            continue
        while jobsite_index_1 < len(unassigned_jobsites):
            # print("\t", unassigned_jobsites[jobsite_index_1], "\n")
            jobsite_index_2 = jobsite_index_1 + 1
            # if second jobsite is too small
            while jobsite_index_2 < len(unassigned_jobsites) - 1 and unassigned_jobsites[jobsite_index_1].get_num_vols_requested() + unassigned_jobsites[jobsite_index_2].get_num_vols_requested() + unassigned_jobsites[len(unassigned_jobsites) - 1].get_num_vols_requested() > max_fill:
                # print("\t\t", unassigned_jobsites[jobsite_index_2], "\n")
                jobsite_index_2 += 1
            # if second jobsite is out of range or is too big
            if jobsite_index_2 >= len(unassigned_jobsites) - 1 or unassigned_jobsites[jobsite_index_1].get_num_vols_requested() + unassigned_jobsites[jobsite_index_2].get_num_vols_requested() + unassigned_jobsites[jobsite_index_2 + 1].get_num_vols_requested() < min_fill:
                jobsite_index_1 += 1
                continue
            while jobsite_index_2 < len(unassigned_jobsites) and jobsite_index_1 < len(unassigned_jobsites) and group_index < len(unassigned_groups) and len(unassigned_jobsites) > 2:
                # print("\t\t", unassigned_jobsites[jobsite_index_2], "\n")
                jobsite_index_3 = jobsite_index_2 + 1
                while jobsite_index_3 < len(unassigned_jobsites) and unassigned_jobsites[jobsite_index_1].get_num_vols_requested() + unassigned_jobsites[jobsite_index_2].get_num_vols_requested() + unassigned_jobsites[jobsite_index_3].get_num_vols_requested() > max_fill:
                    # print("\t\t\t", unassigned_jobsites[jobsite_index_3], "\n")
                    jobsite_index_3 += 1
                if jobsite_index_3 < len(unassigned_jobsites) and unassigned_jobsites[jobsite_index_1].get_num_vols_requested() + unassigned_jobsites[jobsite_index_2].get_num_vols_requested() + unassigned_jobsites[jobsite_index_3].get_num_vols_requested() >= min_fill:
                    # print("\t\t\t", unassigned_jobsites[jobsite_index_3], "\n")
                    unassigned_jobsites[jobsite_index_1].add_group(unassigned_groups[group_index])
                    unassigned_jobsites[jobsite_index_2].add_group(unassigned_groups[group_index])
                    unassigned_jobsites[jobsite_index_3].add_group(unassigned_groups[group_index])
                    unassigned_groups[group_index].add_jobsite(unassigned_jobsites[jobsite_index_1])
                    unassigned_groups[group_index].add_jobsite(unassigned_jobsites[jobsite_index_2])
                    unassigned_groups[group_index].add_jobsite(unassigned_jobsites[jobsite_index_3])

                    assigned_jobsites.append(copy.deepcopy(unassigned_jobsites[jobsite_index_1]))
                    assigned_jobsites.append(copy.deepcopy(unassigned_jobsites[jobsite_index_2]))
                    assigned_jobsites.append(copy.deepcopy(unassigned_jobsites[jobsite_index_3]))
                    del unassigned_jobsites[jobsite_index_3]
                    del unassigned_jobsites[jobsite_index_2]
                    del unassigned_jobsites[jobsite_index_1]

                    assigned_groups.append(copy.deepcopy(unassigned_groups[group_index]))
                    del unassigned_groups[group_index]
                    flag = True
                    break
                elif jobsite_index_3 < len(unassigned_jobsites) and jobsite_index_3 == jobsite_index_2 + 1:
                        if jobsite_index_2 == jobsite_index_1 + 1:
                            group_index += 1
                            flag = True
                            break
                        jobsite_index_1 += 1
                        if jobsite_index_1 > len(unassigned_jobsites):
                            group_index += 1
                            flag = True
                        break
                jobsite_index_2 += 1
                if jobsite_index_2 >= len(unassigned_jobsites) - 1:
                    jobsite_index_1 += 1
                    if jobsite_index_1 > len(unassigned_jobsites) - 2:
                            group_index += 1
                            flag = True
                    break
            if flag:
                flag = False
                break 
    unassigned_jobsites.sort()
    unassigned_groups.sort()

def to_excel(name):
    wb = Workbook()
    # make sheet to display the assigned groups and jobsites
    sheet_assigned = wb.add_sheet('Assigned') 
    # create headers
    sheet_assigned.write(0, 0, 'Organization Name')
    sheet_assigned.write(0, 1, 'Organization ID')
    sheet_assigned.write(0, 2, 'Number Group Volunteers')
    sheet_assigned.write(0, 3, 'Jobsite ID')

    sheet_assigned.write(0, 5, 'Jobsite ID')
    sheet_assigned.write(0, 6, 'Jobsite Name')
    sheet_assigned.write(0, 7, 'Number Jobsite Volunteers Requested')
    sheet_assigned.write(0, 8, 'Number Volunteers Assigned')
    sheet_assigned.write(0, 9, 'Fill Percentage')
    # write out group data
    row = 1
    for group in assigned_groups:
        for jobsite_idx, jobsite in enumerate(group.get_jobsites()):
            if len(group.get_jobsites()) > 1:
                split_name = group.get_name() + " " + str(jobsite_idx + 1)
                sheet_assigned.write(row, 0, split_name)
            else: 
                sheet_assigned.write(row, 0, group.get_name())
            sheet_assigned.write(row, 1, group.get_ID())

            sheet_assigned.write(row, 2, jobsite.get_num_vols_assigned())
            sheet_assigned.write(row, 3, jobsite.get_ID())
            row += 1

    # write assigned jobsite data
    row = 1
    for jobsite in assigned_jobsites:
        sheet_assigned.write(row, 5, jobsite.get_ID())
        sheet_assigned.write(row, 6, jobsite.get_name())
        sheet_assigned.write(row, 7, jobsite.get_num_vols_requested())
        sheet_assigned.write(row, 8, jobsite.get_num_vols_assigned())
        sheet_assigned.write(row, 9, jobsite.get_fill_percent())
        row += 1

    # write unassigned data
    sheet_unassigned_jobsites = wb.add_sheet('Unassigned Jobsites') 
    sheet_unassigned_jobsites.write(0, 0, 'Jobsite ID')
    sheet_unassigned_jobsites.write(0, 1, 'Jobsite Name')
    sheet_unassigned_jobsites.write(0, 2, 'Number Jobsite Volunteers Requested')
    sheet_unassigned_jobsites.write(0, 3, 'Fill Percentage')
    for idx, jobsite in enumerate(unassigned_jobsites):
        sheet_unassigned_jobsites.write(idx + 1, 0, jobsite.get_ID())
        sheet_unassigned_jobsites.write(idx + 1, 1, jobsite.get_name())
        sheet_unassigned_jobsites.write(idx + 1, 2, jobsite.get_num_vols_requested())
        sheet_unassigned_jobsites.write(idx + 1, 3, jobsite.get_fill_percent())

    sheet_unassigned_groups = wb.add_sheet('Unassigned Groups') 
    sheet_unassigned_groups.write(0, 0, 'Organization Name')
    sheet_unassigned_groups.write(0, 1, 'Organization ID')
    sheet_unassigned_groups.write(0, 2, 'Number Group Volunteers')
    for idx, group in enumerate(unassigned_groups):
        sheet_unassigned_groups.write(idx + 1, 0, group.get_name())
        sheet_unassigned_groups.write(idx + 1, 1, group.get_ID())
        sheet_unassigned_groups.write(idx + 1, 2, group.get_num_vols())

    wb.save(name)

def calculate_error():
    # go through all assigned jobsites calculating the over- or underallocation
    error = 0.0
    for jobsite in assigned_jobsites:
        error += abs(jobsite.get_fill_percent() - FILL_PERCENT)
    return error

def calculate_permutation(permutation, diverging_index=0, previous_partial_results=[[None, None, None, None] for _ in range(10)]):
    # go through every permutation, running each algorithm
    for x in range (diverging_index, len(permutation)):
        if permutation[x][0] == 0:
            match1to1_over(permutation[x][1])
        elif permutation[x][0] == 1:
            match2to1_over(permutation[x][1])
        elif permutation[x][0] == 2:
            match1to2_over(permutation[x][1])
        elif permutation[x][0] == 3:
            match3to1_over(permutation[x][1])
        elif permutation[x][0] == 4:
            match1to3_over(permutation[x][1])
        elif permutation[x][0] == 5:
            match1to1_under(permutation[x][1])
        elif permutation[x][0] == 6:
            match2to1_under(permutation[x][1])
        elif permutation[x][0] == 7:
            match1to2_under(permutation[x][1])
        elif permutation[x][0] == 8:
            match3to1_under(permutation[x][1])
        elif permutation[x][0] == 9:
            match1to3_under(permutation[x][1])
        elif permutation[x][0] == 10:
            match1to1_forward(permutation[x][1])
        elif permutation[x][0] == 11:
            match2to1_forward(permutation[x][1])
        elif permutation[x][0] == 12:
            match1to2_forward(permutation[x][1])
        elif permutation[x][0] == 13:
            match3to1_forward(permutation[x][1])
        elif permutation[x][0] == 14:
            match1to3_forward(permutation[x][1])
        elif permutation[x][0] == 15:
            match1to1_backward(permutation[x][1])
        elif permutation[x][0] == 16:
            match2to1_backward(permutation[x][1])
        elif permutation[x][0] == 17:
            match1to2_backward(permutation[x][1])
        elif permutation[x][0] == 18:
            match3to1_backward(permutation[x][1])
        elif permutation[x][0] == 19:
            match1to3_backward(permutation[x][1])

        previous_partial_results[x][0] = copy.deepcopy(unassigned_jobsites)
        previous_partial_results[x][1] = copy.deepcopy(unassigned_groups)
        previous_partial_results[x][2] = copy.deepcopy(assigned_jobsites)
        previous_partial_results[x][3] = copy.deepcopy(assigned_groups)

    return previous_partial_results

def find_optimal_permutation(permutations, jobsites_from_file, groups_from_file):
    # establish that we're using the global variables rather than local
    global unassigned_jobsites
    global unassigned_groups
    global assigned_jobsites
    global assigned_groups
    
    # initialize all values to extremes so that they will be overwritten
    min_tot_unassigned = len(unassigned_groups) + len(unassigned_jobsites)
    min_error = float('inf')
    optimal_permutation = permutations[0]

    # initialize previous (which is nonexistent because we start at the first)
    previous_permutation = [None for _ in range(len(permutations[0]))]
    previous_partial_results = [[None, None, None, None] for _ in range(len(previous_permutation))]
    
    # go through every permutation
    for idx, permutation in enumerate(permutations):
        print("Running permutation: ", permutation)
        coupled_idx = enumerate(zip(previous_permutation, permutation)) 
        diverging_index = next( (idx for idx, (x, y) in coupled_idx if x!=y) ) # find where this permutation deviates from the last
        # if there is some overlap in the current permutation with the last permutation, reload that overlap
        if diverging_index != 0:
            unassigned_jobsites = copy.deepcopy(previous_partial_results[diverging_index - 1][0])
            unassigned_groups = copy.deepcopy(previous_partial_results[diverging_index - 1][1])
            assigned_jobsites = copy.deepcopy(previous_partial_results[diverging_index - 1][2])
            assigned_groups = copy.deepcopy(previous_partial_results[diverging_index - 1][3])
        # if there is no overlap, read from the file 
        else: 
            # delete old data
            unassigned_jobsites = copy.deepcopy(jobsites_from_file)
            unassigned_groups = copy.deepcopy(groups_from_file)
            del assigned_jobsites[:]
            del assigned_groups[:]

        # go through each permutation, calculating the new matches and storing results after each algorithm
        previous_partial_results = calculate_permutation(permutation, diverging_index, previous_partial_results)
            
        # if there is a new min (either less unassigned or same unassigned and less error)
        if len(unassigned_groups) + len(unassigned_jobsites) < min_tot_unassigned or (len(unassigned_jobsites) + len(unassigned_groups) == min_tot_unassigned and calculate_error() < min_error):
            optimal_permutation = permutation
            min_tot_unassigned = len(unassigned_groups) + len(unassigned_jobsites)
            print("NEW MIN! ", len(unassigned_jobsites), " unassigned jobsites, ", len(unassigned_groups), "unassigned groups.")
            min_error = calculate_error()
        # print percent complete
        print((idx+1)/len(permutations)*100, "% complete\n")

    return optimal_permutation

def calculate_fill():
    global FILL_PERCENT
    # calculate how many total volunteers were requested by jobsites
    tot_vols_requested = 0
    for i in range(len(unassigned_jobsites)):
        tot_vols_requested = tot_vols_requested + unassigned_jobsites[i].get_num_vols_requested()
    
    # calculate how many total volunteers signed up with organizations (or as individuals)
    tot_vols_available = 0
    for i in range(len(unassigned_groups)):
        tot_vols_available = tot_vols_available + unassigned_groups[i].get_num_vols()
    
    # calculate the overall ratio of volunteers available to volunteers requested
    FILL_PERCENT = tot_vols_available / tot_vols_requested

def read_excel():
    while True:
        try:
            file_name = input("Please enter your excel file name:\n").strip()
            wb = xlrd.open_workbook(file_name)
            break 
        except:
            print("ERROR: File doesn't exist: ", file_name)

    # take in information needed to read group data from excel sheet
    while True:
        try:
            sheet_num = int(input("Please enter which sheet number of the excel document is the sheet with the campus organizations' information.\n\tEx: If it is the first sheet please enter '1'.\n").strip()) - 1
            break
        except:
            print("ERROR! Please enter organization sheet as a number\n")
    while True:
        response = input("Does this sheet contain headings? Please enter 'yes' or 'no'.\n").lower().strip()
        if response == 'yes':
            row = 1
            break
        elif response == 'no':
            row = 0
            break
        else:
            print("ERROR! Please respond 'yes' or 'no'\n")
    while True:
        try:
            name_column = int(input("Please enter which column of the excel document contains the organization names. ENTER AS A NUMBER.\n\tEx: If it is the first column please enter '1'.\n").strip()) - 1
            break
        except:
            print("ERROR! Please enter column as a number\n")
    while True:
        try:
            num_vols_column = int(input("Please enter which column of the excel document contains the number of volunteers signed up with an organization. ENTER AS A NUMBER.\n\tEx: If it is the second column please enter '2'.\n").strip()) - 1
            break
        except: 
            print("ERROR! Please enter column as a number\n")

    # open excel sheet, create Group object, and store in unassigned groups
    group_sheet = wb.sheet_by_index(sheet_num) 
    while row < group_sheet.nrows and group_sheet.cell_value(row, name_column):
        try:
            unassigned_groups.append(Group(row, group_sheet.cell_value(row, name_column), int(group_sheet.cell_value(row, num_vols_column))))
            groups_from_file.append(Group(row, group_sheet.cell_value(row, name_column), int(group_sheet.cell_value(row, num_vols_column))))
            row += 1
        except:
            sys.exit("ERROR! There was a non-number in a cell under the number of volunteers column. Please check over your excel sheet and run algorithm again.\n")

    # take in information needed to read jobsite data from excel sheet
    while True:
        try:
            sheet_num = int(input("Please enter which sheet number of the excel document is the sheet with the jobsite information.\n\tEx: If it is the first sheet please enter '1'.\n").strip()) - 1
            break
        except:
            print("ERROR! Please enter jobsite sheet as a number\n")
    while True:
        response = input("Does this sheet contain headings? Please enter 'yes' or 'no'.\n").lower().strip()
        if response == 'yes':
            row = 1
            break
        elif response == 'no':
            row = 0
            break
        else:
            print("ERROR! Please respond 'yes' or 'no'\n")
    while True:
        try:
            name_column = int(input("Please enter which column of the excel document contains the jobsite names. ENTER AS A NUMBER.\n\tEx: If it is the first column please enter '1'.\n").strip()) - 1
            break
        except:
            print("ERROR! Please enter column as a number\n")
    while True:
        try:
            num_vols_column = int(input("Please enter which column of the excel document contains the number of volunteers requested by a jobsite. ENTER AS A NUMBER.\n\tEx: If it is the second column please enter '2'.\n").strip()) - 1
            break
        except: 
            print("ERROR! Please enter column as a number\n")
    while True:
        id_exists = input("Do your jobsites have ID numbers? Please enter 'yes' or 'no'.\n").lower().strip()
        if id_exists == 'yes':
            while True:
                try:
                    id_column = int(input("Please enter which column of the excel document contains the jobsite IDs. ENTER AS A NUMBER.\n\tEx: If it is the third column please enter '3'.\n").strip()) - 1
                    break
                except: 
                    print("ERROR! Please enter column as a number\n")
            jobsite_sheet = wb.sheet_by_index(sheet_num) 
            while row < jobsite_sheet.nrows and jobsite_sheet.cell_value(row, name_column):
                try:
                    unassigned_jobsites.append(Jobsite(jobsite_sheet.cell_value(row, name_column), int(jobsite_sheet.cell_value(row, num_vols_column)), int(jobsite_sheet.cell_value(row, id_column))))
                    jobsites_from_file.append(Jobsite(jobsite_sheet.cell_value(row, name_column), int(jobsite_sheet.cell_value(row, num_vols_column)), int(jobsite_sheet.cell_value(row, id_column))))
                    row += 1
                except:
                    sys.exit("ERROR! There was a non-number in a cell under either the number of volunteers requested column or the ID column. Please check over your excel sheet and run algorithm again.\n")
            break
        elif id_exists == 'no':
            while row < jobsite_sheet.nrows and jobsite_sheet.cell_value(row, name_column):
                try:
                    unassigned_jobsites.append(Jobsite(jobsite_sheet.cell_value(row, name_column), int(jobsite_sheet.cell_value(row, num_vols_column))))
                    jobsites_from_file.append(Jobsite(jobsite_sheet.cell_value(row, name_column), int(jobsite_sheet.cell_value(row, num_vols_column))))
                    row += 1
                except:
                    sys.exit("ERROR! There was a non-number in a cell under the number of volunteers requested column. Please check over your excel sheet and run algorithm again.\n")
            break
        else:
            print("ERROR! Please enter 'yes' or 'no'\n")

    jobsites_from_file.sort()
    groups_from_file.sort()
    unassigned_groups.sort()
    unassigned_jobsites.sort()
    return [jobsites_from_file, groups_from_file]

def generate_permutations(permutation_length, list_leniencies):
    algorithms = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19] # each number corresponds to a pairing algorithm.
    algorithm_leniency_pairs = []
    for algorithm in algorithms:
        for leniency in list_leniencies:
            algorithm_leniency_pairs.append([algorithm, leniency]) # create algorithm&leniency combos
    permutations = list(itertools.permutations(algorithm_leniency_pairs, permutation_length)) # generate all permutations of algorithm&leniency combos of specified length

    # go through and remove all unnecessary permutations
    permutation_idx = 0
    deleted = False
    while permutation_idx < len(permutations):
        # remove any permutations that start with a 3to1 or 1to3 becuase they would take 5ever to compute
        if permutations[permutation_idx][0][0] == 3 or permutations[permutation_idx][0][0] == 4 or permutations[permutation_idx][0][0] == 8 or permutations[permutation_idx][0][0] == 9 or permutations[permutation_idx][0][0] == 13 or permutations[permutation_idx][0][0] == 14 or permutations[permutation_idx][0][0] == 18 or permutations[permutation_idx][0][0] == 19: 
            del permutations[permutation_idx]
            continue
        # remove any permutations that have an algorithm&leniency combo following a combo of the same algorithm but higher leniency
        # this is because the first combo (of higher leniency) will pair anything the second could and the second combo (of lower leniency) will make zero pairs
        for alg1_idx in range(len(permutations[permutation_idx]) - 1):
            alg2_idx = alg1_idx + 1
            while alg2_idx < len(permutations[permutation_idx]):
                if ((permutations[permutation_idx][alg1_idx][0] == permutations[permutation_idx][alg2_idx][0]
                        or permutations[permutation_idx][alg1_idx][0] == permutations[permutation_idx][alg2_idx][0] - 5
                            or permutations[permutation_idx][alg1_idx][0] == permutations[permutation_idx][alg2_idx][0] + 5 
                                or permutations[permutation_idx][alg1_idx][0] == permutations[permutation_idx][alg2_idx][0] - 10 
                                    or permutations[permutation_idx][alg1_idx][0] == permutations[permutation_idx][alg2_idx][0] + 10 
                                        or permutations[permutation_idx][alg1_idx][0] == permutations[permutation_idx][alg2_idx][0] - 15 
                                            or permutations[permutation_idx][alg1_idx][0] == permutations[permutation_idx][alg2_idx][0] - 15) 
                                                and permutations[permutation_idx][alg1_idx][1] >= permutations[permutation_idx][alg2_idx][1]):
                    del permutations[permutation_idx]
                    deleted = True
                    break
                alg2_idx += 1
            if deleted:
                break
        if not deleted:
            permutation_idx += 1
        deleted = False
    return permutations

def initialize():
    # make sure excel file is accessible
    while True:
        response = input("Have you imported your excel file of jobsites and organizations to your workspace / project folder? Please enter 'yes' or 'no'.\n").lower().strip()
        if response == 'yes':
            break
        elif response == 'no':
            print("Please import and return to run algorithm after.\n")
        else:
            print("ERROR! Please respond 'yes' or 'no'\n")

    # take in leniencies
    while True:
        response = input("How many various 'leniencies' would you like to enter?\n\tLENIENCIES: Refer to the 'margins of error' you want the algorithm to try when comparing jobsite volunteer needs and organizations' available volunteers.\n\tRECOMMENDED: 1, 2, or 3. THE HIGHER NUMBER YOU ENTER, THE SLOWER THE ALGORITHM BUT THE MORE MATCHES CREATED\n").strip()
        try:
            num_leniencies = int(response)
            break
        except:
            print("ERROR! Please respond with an integer\n")
    list_leniencies = []
    num_entered = 1
    while num_entered <= num_leniencies:
        try:
            print("Please enter leniency #", num_entered, " AS A DECIMAL, not as a percentage!\n\tEx: If you want a 20% leniency, enter 0.2.")
            leniency = float(input("\tNOTE: Higher leniencies will pair more data but will cause more over- and underallocation\n").strip())
            if leniency >= 0 and leniency <= 1:
                list_leniencies.append(leniency)
                num_entered += 1
            else: 
                print("ERROR! Please respond with a number between 0 and 1\n")
        except: 
            print("ERROR! Please respond with a number between 0 and 1\n")

    # take in permutation length
    while True:
        try:
            permutation_length = int(input("How many times would you like each permutation to attempt different types of pairings?\n\tPERMUTATIONS: Refer to the various matching attempts that are ran. Only the optimal solution/(s) are outputted at the end.\n\tTYPES OF PAIRINGS: 1 jobsite to 1 organization, 2 jobsites to 1 organization, 1 jobsite to 2 organizations, 3 to 1, and 1 to 3. Each type is then given a specific leniency when ran.\n\tRECOMMENDED: 3, 4, or 5. THE HIGHER NUMBER YOU ENTER, THE SLOWER THE ALGORITHM BUT THE MORE MATCHES CREATED\n").strip())
            break
        except:
            print("ERROR! Please respond with an integer\n")

    return [permutation_length, list_leniencies]

def main():
    [permutation_length, list_leniencies] = initialize() # asks user to input permutation length and leniencies
    permutations = generate_permutations(permutation_length, list_leniencies) # generates all the permutations of pairing algorithms to be tested

    [jobsites_from_file, groups_from_file] = read_excel() # reads in data to the unassigned groups and jobsites lists
    calculate_fill() # finds the ratio of total volunteers available to total volunteers requested
    optimal_permutation = find_optimal_permutation(permutations, jobsites_from_file, groups_from_file) # tests all the permutations, keeping track of the most optimal
    
    # delete old data
    global unassigned_jobsites
    global unassigned_groups
    unassigned_jobsites = copy.deepcopy(jobsites_from_file)
    unassigned_groups = copy.deepcopy(groups_from_file)
    del assigned_jobsites[:]
    del assigned_groups[:]
    calculate_permutation(optimal_permutation) # calculate the matches from the optimal permutation
    print("Ideal permutation for minimum unmatched: " , optimal_permutation, "\n")
    print("Matches printed to 'Optimal Match.xls'\n")
    to_excel('Optimal Match.xls') # output an excel file of the data

if __name__ == "__main__":
    main()