"""
File     : assignment1.py
Author   : Chenyang Wang
Origin   : Sun Apr 1 10:30:04 2018
Purpose  : Program for implementing a parallelized application to identify
           Instagram activity around Melbourne
"""
import json
import mpi4py.MPI as MPI


# Load the grid box id, latitudes and longitudes of a range of gridded boxes,
# and an integer that stores the posts number into a list.
def load_grid():
    """
    :rtype: List[List[str/float/int]]
    """
    with open("melbGrid.json") as grid_file:
        grids_data = json.load(grid_file)
        grid_list = []
        for k in range(0, 16):
            grid_list.append(
                [grids_data["features"][k]["properties"]["id"],
                 grids_data["features"][k]["properties"]["xmin"],
                 grids_data["features"][k]["properties"]["xmax"],
                 grids_data["features"][k]["properties"]["ymin"],
                 grids_data["features"][k]["properties"]["ymax"],
                 0])
        return grid_list


# For different cores, dispatch different parts of the json file and let them
# load the coordinates(if any) of these instagram posts in to a list separately
def load_instagram(pv, cr, cs):
    """
    :type pv: int
    :type cr: int
    :type cs: int
    :rtype: List[List[float]]
    """
    start_index = cr * pv if cr > 0 else 1
    end_index = (cr+1) * pv if cr < (cs - 1) else -1
    line_index = 0
    instagram_coordinates = []
    with open("bigInstagram.json") as ins_file:
        for ins_line in ins_file:
            line_index += 1
            if end_index != -1 and start_index <= line_index < end_index:
                try:
                    ins_data = json.loads(ins_line[:-2])
                    if ins_data['doc'].get('coordinates'):
                        coordinate = ins_data['doc']['coordinates']['coordinates']
                        instagram_coordinates.append(coordinate)
                except Exception:
                    continue
            elif end_index != -1 and line_index >= end_index:
                break

            if end_index == -1 and line_index >= start_index:
                try:
                    ins_data = json.loads(ins_line[:-2])
                    if ins_data['doc'].get('coordinates'):
                        coordinate = ins_data['doc']['coordinates']['coordinates']
                        instagram_coordinates.append(coordinate)
                except Exception:
                    continue

    return instagram_coordinates


# Get the total number of posts of each grid boxes and put them in a List
def get_posts_number(coordinates_list, grid_list):
    """
    :type coordinates_list: List[List[float]]
    :type grid_list: List[List[str/float/int]]
    :rtype: List[int]
    """
    for coordinate in coordinates_list:
        for grid in grid_list:
            # Some coordinates might be 'Nonetype', so we need the program
            # to be error tolerate
            try:
                x_cd, y_cd = coordinate[1], coordinate[0]
                if grid[1] <= x_cd < grid[2] and grid[3] <= y_cd < grid[4]:
                    grid[5] += 1
                    break
            except TypeError:
                continue
    counter_list = []
    for grid in grid_list:
        counter_list.append(grid[5])
    return counter_list


# Get the number posts of each grid
def get_grid_posts(grids, posts_number):
    """
    :type grids: List[str]
    :type posts_number: List[int]
    :return: List[]
    """
    grid_posts_list = []
    for i in range(len(grids)):
        grid_posts_list.append([grids[i], posts_number[i]])
    return grid_posts_list


# Format the rows, return the total number of posts of each row
def format_rows(grid_posts_list):
    """
    :type grid_posts_list: List[List[str, int]]
    :rtype: List[List[str, int]]
    """
    rows = list()
    rows.append(["A-Row: ", grid_posts_list[0][1] + grid_posts_list[1][1] +
                grid_posts_list[2][1] + grid_posts_list[3][1]])
    rows.append(["B-Row: ", grid_posts_list[4][1] + grid_posts_list[5][1] +
                grid_posts_list[6][1] + grid_posts_list[7][1]])
    rows.append(["C-Row: ", grid_posts_list[8][1] + grid_posts_list[9][1] +
                grid_posts_list[10][1] + grid_posts_list[11][1] +
                grid_posts_list[12][1]])
    rows.append(["D-Row: ", grid_posts_list[13][1] + grid_posts_list[14][1] +
                grid_posts_list[15][1]])

    return rows


# Format the columns, return the total number of posts of each column
def format_columns(grid_posts_list):
    cols = list()
    cols.append(["Column 1: ", grid_posts_list[0][1] + grid_posts_list[4][1] +
                grid_posts_list[8][1]])
    cols.append(["Column 2: ", grid_posts_list[1][1] + grid_posts_list[5][1] +
                 grid_posts_list[9][1]])
    cols.append(["Column 3: ", grid_posts_list[2][1] + grid_posts_list[6][1] +
                 grid_posts_list[10][1] + grid_posts_list[13][1]])

    cols.append(["Column 4: ",
                 grid_posts_list[12][1] + grid_posts_list[15][1]])

    return cols


# Rank the grid boxes based on the total number of posts(from high to low)
def rank(grid_posts_list):
    """
    :type grid_posts_list: List[float]
    :rtype: void
    """
    grid_posts_list.sort(key=lambda x: (-x[1]))
    for grid in grid_posts_list:
        print(str(grid[0]) + ": " + str(grid[1]) + " posts")


# Start using MPI to do the work.
comm = MPI.COMM_WORLD
comm_rank = comm.Get_rank()
comm_size = comm.Get_size()

# Use rank 0 to load the grid data and computes each core's start point of
# reading and parsing the json file.
if comm_rank == 0:
    grid_data = load_grid()
    total_len = 0
    with open("bigInstagram.json") as ins_obj:
        for line in ins_obj:
            total_len += 1
        pivot = total_len // comm_size
else:
    grid_data = None
    pivot = None

# Broadcast the grid coordinates to every core.
grid_data = comm.bcast(grid_data, root=0)
# Broadcast the pivot to every core so they can know from where to read and
# parse their json part.
pivot = comm.bcast(pivot, root=0)
# Each core starts doing their jobs simultaneously and gets the posts number
# of each grid, then the MPI will gather all the results together.
ins_coordinates = load_instagram(pivot, comm_rank, comm_size)
distribute_res = get_posts_number(ins_coordinates, grid_data)
new_res = comm.gather(distribute_res, root=0)

# Use rank 0 to finish the ranking and do some printing as well.
if comm_rank == 0:
    combined_posts = [sum(i) for i in zip(*new_res)]

    grid_ids = ["A1", "A2", "A3", "A4", "B1", "B2", "B3", "B4", "C1", "C2",
                "C3", "C4", "C5", "D3", "D4", "D5"]
    posts_per_grid = get_grid_posts(grid_ids, combined_posts)
    row = format_rows(posts_per_grid)
    col = format_columns(posts_per_grid)
    print("Rank by grid boxes:")
    rank(posts_per_grid)
    print("\nRank by rows:")
    rank(row)
    print("\nRank by columns:")
    rank(col)
