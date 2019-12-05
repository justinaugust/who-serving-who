#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import sqlalchemy as sal
import numpy as np
import altair as alt
from altair.expr import datum
import json
import time
# alt.renderers.enable('notebook')
alt.data_transformers.disable_max_rows()
alt.themes.enable('opaque')


# In[2]:


# host = "localhost"
# dbname = "who_serving_who"
# user = "justinaugust"
# port =  5432

# engine = sal.create_engine(f'postgresql://{user}@{host}:{port}/{dbname}')
conn_string = 'postgres://jcajwqzxmfftxy:05660bb6c45b71f75b905822161c771a8a80aeb74ae4b949c1314409a35b98bc@ec2-54-225-195-3.compute-1.amazonaws.com:5432/dcqg9fqmvhc67i'
engine = sal.create_engine(conn_string)


# In[75]:


with engine.connect() as conn, conn.begin():
    command = sal.sql.text(f"""
    SELECT * FROM caaspp_subgroups
    ;
    """)
    subgroups_df = pd.read_sql(command, con=conn)
    conn.execute("commit")
          
with engine.connect() as conn, conn.begin():
    command = sal.sql.text(f"""
    SELECT * FROM caaspp_tests
    WHERE
        caaspp_tests."Test ID" IN (1,2)
    ;
    """)
    tests_df = pd.read_sql(command, con=conn)
    conn.execute("commit")
            
with engine.connect() as conn, conn.begin():
    command = sal.sql.text(f"""
    SELECT
        DISTINCT(res2019."School Code") as "school_id",
        meta."School Name" as "school_name",
        meta."Street Address" as "address",
        meta."ZIP" as zipcode,
        meta."lat" as "lat",
        meta."lng" as "lng"
    FROM caaspp_2019 as res2019
    INNER JOIN caaspp_2019_entities ent2019 
        ON ent2019."School Code" = res2019."School Code"
    INNER JOIN schools_metadata meta
        ON meta."School ID" = res2019."School Code"
    WHERE res2019."School Code" != 0 AND meta."City" = 'Oakland'
    
    ;
    """)
    meta_df = pd.read_sql(command, con=conn)
    conn.execute("commit")


# In[70]:


sorted_groups = {}
for group in subgroups_df['Student Group'].unique():
    sorted_groups[group] = {}
    for demo in subgroups_df.loc[subgroups_df['Student Group'] == group, 'Demographic Name'].unique():
        sorted_groups[group][demo] = subgroups_df.loc[subgroups_df['Demographic Name'] == demo, 'Demographic ID Num'].values[0]


# In[5]:


html = """"""
for demos in sorted_groups:
    html += f"""<label for="{demos}">{demos}</label><br>
    <select name="{demos}">"""
    for demo, value in sorted_groups[demos].items():
        html += f"""
        <option value="{value}">{demo}</option>
        """
    html += f"""</select><hr>
    """


# # Deviation from All Students Proficiencies by Demo at City Level

# In[73]:


def get_total_tested(school_level):
    disagg_scores = get_disagg_scores(school_level)
    disagg_scores = disagg_scores.merge(meta_df)
    dfs = []


    for subgroup in disagg_scores.subgroup_id.unique():
        for test_id in disagg_scores.test_id.unique():
            mask = (disagg_scores['subgroup_id'] == subgroup) &             (disagg_scores['test_id'] == test_id)

            tot_sub_tested = disagg_scores.loc[mask, 'total_tested'].sum()
            sub_tested = disagg_scores.loc[mask, 'total_tested']
            perc_tested = sub_tested / tot_sub_tested
            disagg_scores.loc[mask,'perc_tested'] = perc_tested

    df1 = disagg_scores.groupby(by=['test_id', 'subgroup_id'])[['total_tested']].sum()
    df2 = disagg_scores.groupby(by=['test_id', 'subgroup_id'])[['prof_above']].mean()
    total_tested = pd.concat([df1,df2], axis=1, )

    total_tested.reset_index(inplace=True)

    for subgroup in total_tested.subgroup_id.unique():
        for test_id in total_tested.test_id.unique():

            all_students = total_tested.loc[(total_tested['test_id'] == test_id) &              (total_tested['subgroup_id'] == 1), 'prof_above'].values[0]

            sub_prof = total_tested.loc[(total_tested['test_id'] == test_id) &                          (total_tested['subgroup_id'] == subgroup), 'prof_above'].values[0]
            total_tested.loc[(total_tested['test_id'] == test_id) &                          (total_tested['subgroup_id'] == subgroup), 'demo_diff'] = sub_prof - all_students
    return(total_tested)


# # Create Background Map

# In[72]:


oakland_url = 'https://data.oaklandnet.com/api/geospatial/9bhq-yt6w?method=export&format=GeoJSON'
oakland = alt.topo_feature(oakland_url, feature = 'Oakland')

oakland_map = alt.Chart(oakland).mark_geoshape(
    fill='lightgray',
    stroke='darkgray'
).properties(
#     title = f'Schools in Oakland'
).project('albersUsa')


# # Create Selectors to Highlight Information & Demographic Changes

# In[13]:





# # Maps by School Level

# In[68]:


def get_disagg_scores(school_level):
    with engine.connect() as conn, conn.begin():
        command = sal.sql.text(f"""

        SELECT
            res_2019."School Code" as school_id,
            meta."School Name" AS school_name,
            res_2019."Test Id" AS test_id,
            test_info."Test Name" AS test,
            subgroups."Student Group" AS demographic_group,
            subgroups."Demographic Name" AS demographic,
            res_2019."Subgroup ID" AS subgroup_id,

            CASE
                WHEN CAST(meta."Low Grade*" AS FLOAT) >= 9 THEN 'high'
                WHEN CAST(meta."Low Grade*" AS FLOAT) >=5 AND 
                        CAST(meta."High Grade*" AS FLOAT) <= 9 THEN 'middle'
                Else 'elementary'
                END AS school_level,
            AVG(CAST(res_2019."Percentage Standard Met and Above" AS FLOAT)) 
                AS prof_above,
            SUM(res_2019."Total Tested with Scores") AS total_tested
            FROM caaspp_2019 as res_2019
            INNER JOIN schools_metadata AS meta
                ON meta."School ID" = res_2019."School Code"
            INNER JOIN caaspp_subgroups AS subgroups
                ON subgroups."Demographic ID" = res_2019."Subgroup ID"
            INNER JOIN caaspp_tests AS test_info
                ON test_info."Test ID" = res_2019."Test Id"
            WHERE
                CAST(meta."Low Grade*" AS FLOAT) > -1 AND
                CASE
                        WHEN CAST(meta."Low Grade*" AS FLOAT) >= 9 THEN 'high'
                        WHEN CAST(meta."Low Grade*" AS FLOAT) >=5 AND 
                                    CAST(meta."High Grade*" AS FLOAT) <= 9 THEN 'middle'
                        Else 'elementary'
                        END = '{school_level}'
            GROUP BY school_id, school_name, school_level, test_id, test, demographic_group, subgroup_id, demographic
        ;
        """)
        disagg_scores = pd.read_sql(command, con=conn)
        conn.execute("commit")
    disagg_scores = disagg_scores.merge(meta_df)
    return(disagg_scores)


# In[129]:


def school_level_map(school_level):
    oakland_url = 'https://data.oaklandnet.com/api/geospatial/9bhq-yt6w?method=export&format=GeoJSON'
    oakland = alt.topo_feature(oakland_url, feature = 'Oakland')

    oakland_map = alt.Chart(oakland).mark_geoshape(
        fill='lightgray',
        stroke='darkgray'
    ).properties(
    #     title = f'Schools in Oakland'
    ).project('albersUsa')
    
    schools = get_disagg_scores(school_level)
    school_selector = alt.selection(type = 'single',
                         empty='all',
                         fields=['school_name'],
                        )



    highlight = alt.selection(type = 'single',
                              on = 'mouseover',
                              fields = ['school_name'],
                              )


    tests = list(tests_df['Test Name'].unique())
    tests_dropdown = alt.binding_radio(options = tests,
                                 name = "Which Test?\n",
                                      )
    tests_select = alt.selection(type = "single",
                                  empty = "all",
                                  fields = ['test'],
                                 bind = tests_dropdown,
                                clear = "dblclick")


    filters = {}
    for demo in sorted_groups.keys():
        filters[demo] = {}
        filters[demo]["values"] = list(sorted_groups[demo].keys())
        filters[demo]["selecter"] = alt.binding_select(options = filters[demo]["values"],
                                                      name = f'{demo}\n'
                                                     )
        filters[demo]["select"] = alt.selection(type = "single",
                                      empty = 'all',
                                      fields = ['demographic'],
                                     bind = filters[demo]["selecter"],
                                    name = f'{demo}\n'
                                               )


    
    schools_dots = alt.Chart(schools).mark_circle().encode(
        longitude = 'lng:Q',
        latitude= 'lat:Q',


        size = alt.condition(~highlight,
                            alt.value(250),
                            alt.value(600)
                            ),
        color = alt.Color('average(prof_above):Q',
                          title = 'Average Performance at School',
                  scale = alt.Scale(scheme = 'spectral'),
                 ),
        tooltip = [
            alt.Tooltip(
                'school_name:N',
                title = 'School',
            ),
            alt.Tooltip(
                'address:N',
                title = 'Address',
            ),
            alt.Tooltip(
                'school_level:N',
                title = 'School Level',
            ),
            alt.Tooltip(
                'average(prof_above):Q',
                title = 'Averaged Equity Score',
            ),
        ],
    )

    map_dots = alt.layer(oakland_map,
                         schools_dots.add_selection(filters["Disability Status"]['select']).transform_filter(filters["Disability Status"]['select']
                    ).add_selection(filters["English-Language Fluency"]['select']).transform_filter(filters["English-Language Fluency"]['select']
                    ).add_selection(filters["Economic Status"]['select']).transform_filter(filters["Economic Status"]['select']
                    ).add_selection(filters["Ethnicity"]['select']).transform_filter(filters["Ethnicity"]['select']
                    ).add_selection(filters["Parent Education"]['select']).transform_filter(filters["Parent Education"]['select']
                    ).add_selection(filters["Gender"]['select']).transform_filter(filters["Gender"]['select']
                    ).add_selection(tests_select).transform_filter(tests_select
                    ).add_selection(highlight
                    ))

    map_dots.save(f'static/charts/{school_level}.json')


# # Maps by Identity

# In[69]:


def get_schools(identity = {'all_students':1}, school_level = ['elementary','middle','high']):
    groups = list(identity.values())
    try:
        groups.remove(False)
    except:
        pass
    groups =  "'" + "', '".join(list(map(str,groups))) + "'"
    if type(school_level) == list:
        school_level = "'" + "', '".join(map(str, school_level)) + "'"
    else:
        school_level = "'" + school_level +"'"

    with engine.connect() as conn, conn.begin():
        command = sal.sql.text(f"""
        
        
        SELECT 
            meta."School Name" AS school_name,
            scores_1.school_level AS school_level,
            scores_1.prof_above AS test_1_prof_above,
            scores_2.prof_above AS test_2_prof_above,
            (scores_1.prof_above + scores_2.prof_above)/2 as eq_score,
            meta."Street Address" AS address,
            meta."ZIP" AS zipcode,
            meta."lat" AS lat,
            meta."lng" AS lng
        FROM
            (SELECT res_2019."School Code" AS school_id,
                    CASE
                        WHEN CAST(meta."Low Grade*" AS FLOAT) >= 9 THEN 'high'
                        WHEN CAST(meta."Low Grade*" AS FLOAT) >=5 AND 
                                CAST(meta."High Grade*" AS FLOAT) <= 9 THEN 'middle'
                        Else 'elementary'
                        END
                    AS school_level,
                    AVG(CAST(res_2019."Percentage Standard Met and Above" AS FLOAT)) 
                        AS prof_above
            FROM caaspp_2019 as res_2019
            INNER JOIN schools_metadata meta
                ON meta."School ID" = res_2019."School Code"
            WHERE
                CAST(meta."Low Grade*" AS FLOAT) > -1 AND
                CASE
                        WHEN CAST(meta."Low Grade*" AS FLOAT) >= 9 THEN 'high'
                        WHEN CAST(meta."Low Grade*" AS FLOAT) >=5 AND 
                                    CAST(meta."High Grade*" AS FLOAT) <= 9 THEN 'middle'
                        Else 'elementary'
                        END IN ({school_level})
                AND res_2019."Subgroup ID" IN ({groups})
                AND res_2019."Test Id" = 1
            GROUP BY school_id, school_level) as scores_1
        INNER JOIN
            (SELECT res_2019."School Code" AS school_id,
                    CASE
                        WHEN CAST(meta."Low Grade*" AS FLOAT) >= 9 THEN 'high'
                        WHEN CAST(meta."Low Grade*" AS FLOAT) >=5 AND 
                                CAST(meta."High Grade*" AS FLOAT) <= 9 THEN 'middle'
                        Else 'elementary'
                        END
                    AS school_level,
                    AVG(CAST(res_2019."Percentage Standard Met and Above" AS FLOAT)) 
                        AS prof_above
            FROM caaspp_2019 as res_2019
            INNER JOIN schools_metadata meta
                ON meta."School ID" = res_2019."School Code"
            WHERE
                CAST(meta."Low Grade*" AS FLOAT) > -1 AND
                CASE
                        WHEN CAST(meta."Low Grade*" AS FLOAT) >= 9 THEN 'high'
                        WHEN CAST(meta."Low Grade*" AS FLOAT) >=5 AND 
                                    CAST(meta."High Grade*" AS FLOAT) <= 9 THEN 'middle'
                        Else 'elementary'
                        END IN ({school_level})
                AND res_2019."Subgroup ID" IN ({groups})
                AND res_2019."Test Id" = 2
            GROUP BY school_id, school_level) as scores_2
            ON scores_2.school_id = scores_1.school_id

        INNER JOIN caaspp_2019_entities ent_2019 
            ON ent_2019."School Code" = scores_1.school_id
        INNER JOIN schools_metadata meta
            ON meta."School ID" = scores_1.school_id
        WHERE meta."City" = 'Oakland'
        GROUP BY scores_1.school_id, scores_1.school_level, scores_1.prof_above, scores_2.prof_above,
            meta."School Name",
            meta."Street Address",
            meta."ZIP",
            meta."lat",
            meta."lng"
        ORDER BY eq_score DESC, scores_1.prof_above DESC, scores_2.prof_above DESC
        ;
        """)
        df = pd.read_sql(command, con=conn)
        conn.execute("commit")
        

        return(df)


# In[96]:


def display(identity = {'all_students':1}, school_level = ['elementary','middle','high']):
    oakland_url = 'https://data.oaklandnet.com/api/geospatial/9bhq-yt6w?method=export&format=GeoJSON'
    oakland = alt.topo_feature(oakland_url, feature = 'Oakland')
    
    schools = get_schools(identity, school_level = school_level)
    
    school_selector = alt.selection(type = 'single',
                         empty='all',
                         fields=['school_name'],
                        )



    highlight = alt.selection(type = 'single',
                              on = 'mouseover',
                              fields = ['school_name'],
                              )


    tests = list(tests_df['Test Name'].unique())
    tests_dropdown = alt.binding_radio(options = tests,
                                 name = "Which Test?\n",
                                      )
    tests_select = alt.selection(type = "single",
                                  empty = "all",
                                  fields = ['test'],
                                 bind = tests_dropdown,
                                clear = "dblclick")


    filters = {}
    for demo in sorted_groups.keys():
        filters[demo] = {}
        filters[demo]["values"] = list(sorted_groups[demo].keys())
        filters[demo]["selecter"] = alt.binding_select(options = filters[demo]["values"],
                                                      name = f'{demo}\n'
                                                     )
        filters[demo]["select"] = alt.selection(type = "single",
                                      empty = 'all',
                                      fields = ['demographic'],
                                     bind = filters[demo]["selecter"],
                                    name = f'{demo}\n'
                                               )
        
    total_tested = get_total_tested(school_level[0])
    test1_all_stud_prof = total_tested.loc[(total_tested['subgroup_id'] == 1) & (total_tested['test_id'] == 1), 'prof_above'].values[0]
    test2_all_stud_prof = total_tested.loc[(total_tested['subgroup_id'] == 1) & (total_tested['test_id'] == 2), 'prof_above'].values[0]
    eq_all_stud_prof = (test1_all_stud_prof + test2_all_stud_prof)/2
    schools['test_1_demo_diff'] = schools['test_1_prof_above'].map(lambda x: x - test1_all_stud_prof)
    schools['test_2_demo_diff'] = schools['test_2_prof_above'].map(lambda x: x - test2_all_stud_prof)
    schools['eq_demo_diff'] = schools['eq_score'].map(lambda x: x - eq_all_stud_prof)

    oakland_map = alt.Chart(oakland).mark_geoshape(
        fill='lightgray',
        stroke='darkgray'
    ).properties(
        title = f'{school_level[0].title()} Schools in Oakland'
    ).project('albersUsa')




    selector = alt.selection(type = 'single',
                             empty='all',
                             fields=['school_name'],
                            )
    
    highlight = alt.selection(type = 'single',
                              on = 'mouseover',
                              fields = ['school_name'],
                              )

    
    
    schools_chart = alt.Chart(schools).mark_circle().encode(
        longitude = 'lng:Q',
        latitude= 'lat:Q',
        size = alt.condition(~highlight,
                            alt.value(250),
                            alt.value(600)
                            ),
        color = alt.Color('eq_score:Q',
                          title = 'Equity Score',
                          scale = alt.Scale(scheme = 'spectral'),
                          bin = alt.Bin(extent=([0,100]),
                                        step = 15,
                                          )
                         ),


        tooltip = [
            alt.Tooltip(
                'school_name:N',
                title = 'School',
            ),
            alt.Tooltip(
                'address:N',
                title = 'Address',
            ),
            alt.Tooltip(
                'school_level:N',
                title = 'School Level',
            ),
            alt.Tooltip(
                'eq_score:Q',
                title = 'Balanced Equity Score',
            ),
        ],



    ).add_selection(
        selector
    ).add_selection(
        highlight
    )

    perform = alt.Chart(schools.head(20)).mark_bar().encode(
        y = alt.Y('school_name:N',
            type = 'nominal',
            title = ''
        ),

        x = alt.X('eq_demo_diff:Q',
            type = 'quantitative',
            title = '',
        ),

        color = alt.condition(
            alt.datum.eq_demo_diff > 10,
            alt.value("green"),
            alt.value("red")
        ),


        tooltip = [
            alt.Tooltip(
                'school_name:N',
                title = 'School',
            ),
            alt.Tooltip(
                'eq_score:Q',
                title = 'Balanced Equity Score',
            ),
            alt.Tooltip(
                'test_1_prof_above',
                title = '% Students Meeting or Exceeding Standard on SBAC Reading Test',

            ),
            alt.Tooltip(
                'test_2_prof_above',
                title = '% Students Meeting or Exceeding Standard on SBAC Math Test',

            )
        ],
    

    ).properties(
        title=f'Top 20 {school_level[0].title()} Schools\' Performance Relative to "All Students" in Oakland'
    )
    

    map_ = alt.layer(oakland_map,schools_chart)
    chart = alt.vconcat(map_, perform)



#     chart.save(f'media/output/{time.time()}.json')
#     map_.save(f'html/my_map.html', embed_options={'renderer':'svg'})
#     return(chart)
    filename = f'{time.time()}.json'
    map_.save(f'static/charts/{filename}')
    with open(f'static/charts/{filename}','r') as f:
        map_json = f.read()
#     return(map_)
    return(map_json)


# In[ ]:




