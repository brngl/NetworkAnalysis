import networkx as nx 
import pandas as pd
import matplotlib.pyplot as plt


# path to cleaned file
EVENTS_ATTENDANCE_CLEANED = "NetworkAnalysis/criminal-activity/datasets/cleaned/mafia_bipartite.csv"
# column names - surname will be useful later when we'd like to group them by family
FULLNAME = "fullname"
#FORENAME =  "forename"
SURNAME = "surname" 
EVENT_ID = "event"
# number of events
NUMB_EVENTS = 47
# who has max degree, who participated to most events

# import cleaned df_events_attendance in pandas df_events_attendanceframe
df_events_attendance = pd.read_csv(EVENTS_ATTENDANCE_CLEANED)
# counting the number events attended per individual - degree - attribute
df_degree = df_events_attendance.groupby([SURNAME, FULLNAME], as_index = False).count()
# change name of column header
df_degree.rename(columns = {EVENT_ID: "eventscount"}, inplace = True)
# get family size
df_family = df_degree[[SURNAME, FULLNAME]].groupby(SURNAME, as_index = False).count()
# color - family size. 1 is a single individual
df_family.rename(columns = {FULLNAME: "familysize"}, inplace = True)
#df_family[df_family["color"] > 1]
# maybe not df_degree = df_degree.merge(df_family, on = [SURNAME])
# create graph object from pd df_events_attendanceframe
B = nx.from_pandas_edgelist(df = df_events_attendance, source = SURNAME, target = EVENT_ID)
# get the two bipartite sets - x will be the indivuals, y the events
X,Y = nx.bipartite.sets(B)
# convert the bipartite graph to a weighted graph of common participation to an event
G = nx.algorithms.bipartite.weighted_projected_graph(B, X)
# set number of events attended as node attribute
df_degree = df_degree.groupby(SURNAME, as_index = False).sum()
df_degree.set_index(SURNAME, inplace = True)
nx.set_node_attributes(G, pd.Series(df_degree["eventscount"], index=df_degree.index).to_dict(), "eventscount")
# set family size as attribute
df_family.set_index(SURNAME, inplace = True)
nx.set_node_attributes(G, pd.Series(df_family["familysize"], index=df_family.index).to_dict(), "familysize")
#G.nodes["Pino"]["color"] = "yellow"
nx.write_gml(G, "NetworkAnalysis/criminal-activity/datasets/graph/family.gml")
# does a numerous family size have more importance in the network as numb of summits attended
df = df_family.join(df_degree)
# familysize 
average_attendance = [df[df["familysize"] == i]["eventscount"].mean()/i for i in [1,2,4,5,6]]
average_attendance_binned = [sum(average_attendance[:2])] + [sum(average_attendance[2:])]
plt.bar(["=< 3", "> 3"], average_attendance_binned , width=0.20, color='b')
plt.title("Average summits attendance vs family size", pad=20)
plt.ylabel("Average attendance ÷ family size")
plt.xlabel("Family size")
plt.tight_layout()
plt.grid(axis='y', alpha=0.65)
plt.savefig('NetworkAnalysis/criminal-activity/images/attendance_vs_fam_size')