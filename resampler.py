#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May  3 22:38:26 2024

@author: leo
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import bisect as bs
from scipy.interpolate import interp1d

###### BACKEND FUNCTIONALITY   ################
###############################################
def find_le(a, x):
    'Find rightmost value less than or equal to x'
    i = bs.bisect_right(a, x)
    if i:
        return a[i-1]
    raise ValueError
    
def find_ge(a, x):
    'Find leftmost item greater than or equal to x'
    i = bs.bisect_left(a, x)
    if i != len(a):
        return a[i]
    #raise ValueError
    
def lin_interp(x_min, x_max, y_min, y_max, new_x):
    ''' Interpolates linearly between two x,y coordinates and returns new y value for
    any give x value between the two points'''
    
    x_dif = x_max - x_min
    y_dif = y_max - y_min
    
    slope = y_dif / x_dif
    
    new_y = y_min + (new_x - x_min) * slope
    
    return new_y

def downscaling(data_S, data_R):
    new_age = []
    new_data = []
    
    x1 = data_S[data_S.columns.values[0]]
    y1 = data_S[data_S.columns.values[1]]
    x2 = data_R[data_R.columns.values[0]]
    y2 = data_R[data_R.columns.values[1]]
    
    for i, j in zip(x2, y2):
        try:
            low_x = find_le(x1, i)
            high_x = find_ge(x1, i)
        except ValueError:
            continue 
        
        if (low_x == i) | (high_x == i):
            ly_x_idx =x1[x1 == low_x].index.tolist() # finds index of that value
            low_y = y1[ly_x_idx].iloc[0]   # searches corresponding y value that matches that index
        
            hy_x_idx =x1[x1 == high_x].index.tolist()    # finds index of that value
            high_y = y1[hy_x_idx].iloc[0]  # searchers corresponding y value that matches that index
            
            new_data.append(low_y)
            new_age.append(i)
               
        elif (high_x != i) and (high_x):
            ly_x_idx =x1[x1 == low_x].index.tolist() # finds index of that value
            low_y = y1[ly_x_idx].iloc[0]   # searches corresponding y value that matches that index
        
            hy_x_idx =x1[x1 == high_x].index.tolist()    # finds index of that value
            high_y = y1[hy_x_idx].iloc[0]  # searchers corresponding y value that matches that index
        
            new_y = lin_interp(float(low_x), float(high_x), float(low_y), float(high_y), float(i))
            new_data.append(new_y)
            new_age.append(i)
            
    interp_data = pd.DataFrame({'interp_age':new_age, 'interp_data':new_data})
    
    return interp_data

#####################################################
########################################################

st.header('Import data series to be resampled in .csv file')
uploaded_files_1 = st.file_uploader("Choose a CSV file", accept_multiple_files=True, key='data')
fig, ax = plt.subplots()
for uploaded_file_1 in uploaded_files_1:
    #Import file and drop na
    data_series = pd.read_csv(uploaded_file_1)
    data_series_na = data_series.dropna()
    
    #Line Chart
    ax.plot(data_series_na.iloc[:,0], data_series_na.iloc[:,1], label='data')
    ax.scatter(data_series_na.iloc[:,0], data_series_na.iloc[:,1])
    ax.set_xlabel(data_series_na.columns[0])
    ax.set_ylabel(data_series_na.columns[1])
    ax.legend(loc='upper right')
    st.pyplot(fig)

st.header('Import reference series in .csv file')
uploaded_files_2 = st.file_uploader("Choose a CSV file", accept_multiple_files=True, key='ref')

for uploaded_file_2 in uploaded_files_2:
    data_ref = pd.read_csv(uploaded_file_2)
    data_ref_na = data_ref.dropna()
    
    #Line Chart
    ax_t = ax.twinx()      
    ax_t.plot(data_ref_na.iloc[:,0], data_ref_na.iloc[:,1], 'r', label='reference')
    ax_t.scatter(data_ref_na.iloc[:,0], data_ref_na.iloc[:,1], c='r')
    ax_t.set_ylabel(data_ref_na.columns[1])
    ax_t.legend(loc='lower right')
    st.pyplot(fig)

col1, col2 = st.columns(2, gap="small") 
   
if st.button("Resample", type="primary"):
    # check existence of data series
    if not data_series_na.empty and not data_ref_na.empty:
        data_rescaled = downscaling(data_series_na,  data_ref_na)
        
        with col1:
            st.table(data_rescaled)
        with col2:
            #Line Chart
            ax.plot(data_rescaled.iloc[:,0], data_rescaled.iloc[:,1], 'orange', label='rescaled')
            ax.scatter(data_rescaled.iloc[:,0], data_rescaled.iloc[:,1], c='orange')
            ax.set_xlabel(data_series_na.columns[0])
            ax.set_ylabel(data_series_na.columns[1])
            ax.legend(loc='upper right')
            st.pyplot(fig)
        
    else:
        st.write("One or more data series are missing")    
    @st.cache_data
    def convert_df(df):
        # IMPORTANT: Cache the conversion to prevent computation on every rerun
        return df.to_csv().encode("utf-8")

    csv = convert_df(data_rescaled)
    with col2:
        st.download_button(
        label="Download data as CSV",
        type="primary",
        data=csv,
        file_name="resampled_data.csv",
        mime="text/csv",
        )



