import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import folium
import os

def connect(path):
    global connection, cursor
    connection = sqlite3.connect(path)
    cursor = connection.cursor()
    cursor.execute(' PRAGMA foreign_keys=ON; ')
    connection.commit()
    return

def main():
    global connection, cursor
    path = "a4.db"
    connect(path)
    count1=0
    count2=0
    count3=0
    count4=0

    while True:
        questions = ["1. Q1",
                     "2. Q2",
                     "3. Q3",
                     "4. Q4",
                     "E. EXIT"]
        for pick in questions:
            print(pick)
        
        print()
        pick = input("Please choose the question: ")

        if pick == "1":
            print()
            print("Question 1 selected... ")
            print()
            count1 = count1 + 1
            question1(count1)
            print()
        elif pick == "2":
            print()
            print("Question 2 selected... ")
            print()
            count2 = count2 + 1
            question2(count2)
            print()
        elif pick == "3":
            print()
            print("Question 3 selected... ")
            print()
            count3 = count3 + 1
            question3(count3)
            print()
        elif pick == "4":
            print()
            print("Question 4 selected... ")
            print()
            count4 = count4 + 1
            question4(count4)
            print()
        elif pick.upper() == "E":
            print()
            print("EXIT...")
            break
        else:
            print()
            print("Invalid Input Number...")
            print()

    connection.commit()
    connection.close()
    return

def question1(count):
    global connection
    # years
    startYear = int(input("Enter start year(YYYY):"))
    endYear = int(input("Enter end year(YYYY):"))
    # check whether input is valid
    if startYear>2018 or startYear > endYear or endYear>2018:
        print("Invalid input, please try again\n")
        question1(count)
        return
    # crime type
    crimeType = input("Enter crime type:")

    # sql
    mysql = '''
            SELECT Month, sum(Incidents_Count) as count
            FROM Crime_Incidents
            WHERE Crime_Type = :crime_Type AND Year BETWEEN :start_Year AND :end_Year
            GROUP BY Month;
            '''
    # data frame
    df = pd.read_sql_query(mysql, connection,None,True, {"crime_Type":crimeType, "start_Year":startYear, "end_Year":endYear})
    barplt = df.plot.bar(x='Month')
    plt.show()
    # save figures
    fig = barplt.get_figure()   
    filename = 'Q1-'+str(count)+'.png'
    # check if file exists
    while os.path.isfile(filename):
        count = count+1
        filename = 'Q1-'+str(count)+'.png'
    fig.savefig(filename)
    plt.close()



def question2(count):
    global connection
    # integer N
    N = int(input("Enter number of locations:"))

    # sql
    Nmost = '''
            SELECT a.Neighbourhood_Name, (CANADIAN_CITIZEN+NON_CANADIAN_CITIZEN+NO_RESPONSE) as popA,
                    coordinates.Latitude, coordinates.Longitude
            FROM Population a
            JOIN (SELECT DISTINCT (CANADIAN_CITIZEN+NON_CANADIAN_CITIZEN+NO_RESPONSE) as pop
                    FROM Population WHERE pop !=0 ORDER BY pop DESC LIMIT :N) b
            ON popA = b.pop
            JOIN Coordinates 
			ON Coordinates.Neighbourhood_Name = a.Neighbourhood_Name
            ORDER BY popA DESC
            '''
    Nleast = '''
            SELECT a.Neighbourhood_Name, (CANADIAN_CITIZEN+NON_CANADIAN_CITIZEN+NO_RESPONSE) as popA,
                    Coordinates.Latitude, Coordinates.Longitude
            FROM Population a
            JOIN (SELECT DISTINCT (CANADIAN_CITIZEN+NON_CANADIAN_CITIZEN+NO_RESPONSE) as pop 
                    FROM Population WHERE pop !=0 ORDER BY pop LIMIT :N) b
            ON popA = b.pop
            JOIN Coordinates 
			ON Coordinates.Neighbourhood_Name = a.Neighbourhood_Name
            ORDER BY popA
            '''
    # data frame
    dfMost = pd.read_sql_query(Nmost, connection,None,True, {"N":N})
    dfLeast = pd.read_sql_query(Nleast, connection,None,True, {"N":N})
    # map 
    # crimson circles are the most, and blue circles are the least 
    m = folium.Map(location=[53.5444, -113.323], zoom_start=11)
    for i in range(len(dfMost)):
        folium.Circle(
            location=[dfMost.iloc[i]['Latitude'], dfMost.iloc[i]['Longitude']],
            popup=dfMost.iloc[i]['Neighbourhood_Name'] + '\n' + 'population:' + str(dfMost.iloc[i]['popA']),
            radius=dfMost.iloc[i]['popA'] * .1,
            color='crimson',
            fill=True,
            fill_color='crimson'
        ).add_to(m)

        folium.Circle(
            location=[dfLeast.iloc[i]['Latitude'], dfLeast.iloc[i]['Longitude']],
            popup=dfLeast.iloc[i]['Neighbourhood_Name'] + '\n' + 'population:'+ str(dfLeast.iloc[i]['popA']),
            radius=dfLeast.iloc[i]['popA'] * .9,
            color='blue',
            fill=True,
            fill_color='blue'
        ).add_to(m)

    filename = 'Q2-'+str(count)+'.html'
    # check if file exists
    while os.path.isfile(filename):
        count = count+1
        filename = 'Q2-'+str(count)+'.html'
    m.save(filename)

def question3(count):
    global connection
    # years
    startYear = int(input("Enter start year(YYYY):"))
    endYear = int(input("Enter end year(YYYY):"))
    # check whether input is valid
    if startYear>2018 or startYear > endYear or endYear>2018:
        print("Invalid input, pleae try again \n")
        question3(count)
        return
    # crime type
    crimeType = input("Enter crime type:")
    # integer N
    N = int(input("Enter number of neighborhoods:"))

    # sql
    mysql = '''
            SELECT c.Neighbourhood_Name as neighbourhood_name, sum(c.Incidents_Count) as crime_count, co.Latitude as latitude, co.Longitude as longitude
            FROM crime_incidents c, coordinates co
            WHERE c.Crime_Type = ? AND c.Year BETWEEN ? AND ? AND c.Neighbourhood_Name = co.Neighbourhood_Name
            GROUP BY c.Neighbourhood_Name
            ORDER BY crime_count DESC LIMIT ?
            '''
    df = pd.read_sql_query(mysql, connection, params = [crimeType, startYear, endYear, N])
    # map
    m = folium.Map(location = [53.5444, -113.323], zoom_start = 11)
    for i in range(len(df)):
        folium.Circle(
            location = [df.iloc[i]['latitude'],df.iloc[i]['longitude']],
            popup = df.iloc[i]['neighbourhood_name'] + '\n' + crimeType + '\nCount: ' + str(df.iloc[i]['crime_count']),
            radius = df.iloc[i]['crime_count'] * 20.0,
            color = 'crimson',
            fill = True,
            fill_color = 'crimson'
        ).add_to(m)

    filename = 'Q3-'+str(count)+'.html'
    # check if file exists
    while os.path.isfile(filename):
        count = count + 1
        filename = 'Q3-'+str(count)+'.html'
    m.save(filename)

def question4(count):
    global connection
    # user input
    startYear = int(input("Enter start year(YYYY):"))
    endYear = int(input("Enter end year(YYYY):"))
    # check whether input is valid
    if startYear>2018 or startYear > endYear or endYear>2018:
        print("Invalid Input, please try again \n")
        question4(count)
        return
    # user input
    N = int(input("Enter number of neighborhoods:"))

    # sql 
    mysql1 = '''
        SELECT c.Neighbourhood_Name as neighbourhood_name, crime_count, sumPopulation,(d.crime_count*1.0/d.sumPopulation) as ratio, co.Latitude as latitude, co.Longitude as longitude
        FROM Crime_Incidents c, Coordinates co, 
        (SELECT c2.Neighbourhood_Name, sum(c2.Incidents_Count) as crime_count, (p.CANADIAN_CITIZEN + p.NON_CANADIAN_CITIZEN + p.NO_RESPONSE) as sumPopulation
         FROM Crime_Incidents c2, Population p
         WHERE c2.Neighbourhood_Name = p.Neighbourhood_Name AND c2.Year BETWEEN ? AND ?
         GROUP BY c2.Neighbourhood_Name, sumPopulation
        ) as d
        WHERE  c.Neighbourhood_Name = co.Neighbourhood_Name AND d.Neighbourhood_Name = co.Neighbourhood_Name
        GROUP BY c.Neighbourhood_Name, sumPopulation
        ORDER BY ratio DESC LIMIT ?
        '''
    mysql2 = '''
            SELECT new.type as newType
            FROM (SELECT C.Crime_type as type, sum(c.Incidents_Count) as sumCount
                  FROM Crime_Incidents c
                  WHERE c.Neighbourhood_Name = ?
                  GROUP BY c.Crime_Type
            ) as new
            WHERE new.sumCount in
            (SELECT sum(c2.Incidents_Count)
             FROM Crime_Incidents c2
             WHERE c2.Neighbourhood_Name = ?
             GROUP BY c2.Crime_Type
             ORDER BY sum(c2.Incidents_Count) DESC LIMIT 1
            )
        '''
    # the query try to find the neighbourhood name and order by ratio
    df = pd.read_sql_query(mysql1, connection, params = [startYear,endYear,N])

    m = folium.Map(location = [53.5444, -113.323], zoom_start = 11)
    for i in range(len(df)):
        # the query try to find the most frequent crime type in each of these neighbourhoods we found in the previous query
        df2 = pd.read_sql_query(mysql2, connection, params = [df.iloc[i]['neighbourhood_name'],df.iloc[i]['neighbourhood_name']])

        folium.Circle(
            # location
            location = [df.iloc[i]['latitude'],df.iloc[i]['longitude']],
            # popup text
            popup = df.iloc[i]['neighbourhood_name'] + '\nRatio: ' + str(df.iloc[i]['ratio']) + '\nType: ' + df2.iloc[0]['newType'],
            # size of the radius
            radius = df.iloc[i]['ratio'] * 20.0,
            # color of the radius
            color = 'crimson',
            # whether to fill the map
            fill = True,
            # color to fill with
            fill_color = 'crimson'
        ).add_to(m)

    # create filename
    filename = 'Q4-'+str(count)+'.html'
    # if we quit the program, next time we open the program and save file will not replace the previous file we created
    while os.path.isfile(filename):
        count = count + 1
        filename = 'Q4-'+str(count)+'.html'
    # save the file
    m.save(filename)



if __name__ == "__main__":
    main()