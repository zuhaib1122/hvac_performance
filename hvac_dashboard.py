import numpy as np
import datetime as dt
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st          
#import openpyexcel

# page configuration
st.set_page_config(page_title='HVAC dashboard', layout='wide')
# upload the file
@ st.cache_data
def upload_data(path):
    data = pd.read_csv(path)
    return data
# read the file
st.markdown("<h3 style = 'text-align: center;'>HVAC Chiller Performance </h3>", unsafe_allow_html=True)
df = upload_data("C:/Users/riaz sons/Documents/chiller_project/Professional_ReportOrDashboard_template/HVAC_ML/HVAC Energy Data.csv")
# change date type
df['Local Time (Timezone : GMT+8h)'] = pd.to_datetime(df['Local Time (Timezone : GMT+8h)'])
col_left, col_center, col_right = st.columns([1,1,1], gap='small')
with col_center:
    with st.expander('DataSet Overview'):
        st.dataframe(df.head(5), hide_index=True)
    st.write("*NOTE:* Expand the above **DataSet Overview** button to see the first few rows of **HVAC Energy Data**.")
    with st.container(border=True):
        st.write(f"There are **{df.isnull().sum().sum()}** null values & **{df.duplicated().sum()}** duplicates in dataset.")
df['Hour'] = df['Local Time (Timezone : GMT+8h)'].dt.hour
df['Day'] = df['Local Time (Timezone : GMT+8h)'].dt.day_name()
df['Date'] = df['Local Time (Timezone : GMT+8h)'].dt.date
df['Month'] = df['Local Time (Timezone : GMT+8h)'].dt.month_name()
df['Building_Load (%)'] = (df['Building Load (RT)'] / df['Building Load (RT)'].max()) * 100
df['Energy_Consumption (%)'] = (df['Chiller Energy Consumption (kWh)'] / df['Chiller Energy Consumption (kWh)']) * 100
peak_hour = df.groupby(['Hour']).agg({'Building_Load (%)': 'mean', 'Chiller Energy Consumption (kWh)': 'sum'}).round(2).reset_index().sort_values(by = ['Chiller Energy Consumption (kWh)', 'Building_Load (%)'], ascending=False)
peak_date = df.groupby(['Date']).agg({'Building_Load (%)': 'mean', 'Chiller Energy Consumption (kWh)': 'sum'}).round(2).reset_index().sort_values(by = ['Chiller Energy Consumption (kWh)', 'Building_Load (%)'], ascending=False)
st.markdown("<h3 style = 'text-align: center;'>Peak Load Days & Time </h3>", unsafe_allow_html=True)
# create layout of date
col_a, col_b = st.columns([4,4], gap='medium', wrap=False)
with col_a:
    st.markdown("#### Highest Energy Consumption Days")
    st.dataframe(peak_date.head(5),use_container_width=True, hide_index=True)
with col_b:
    st.markdown("#### Lowest Energy Consumption Days")
    st.dataframe(peak_date.tail(5),use_container_width=True, hide_index=True)

# create layout of hour
col_c, col_d = st.columns([4,4], gap='medium', wrap=False)
with col_c:
    st.markdown("#### Highest Energy Consumption Hours")
    st.dataframe(peak_hour.head(5),use_container_width=True, hide_index=True)
with col_d:
    st.markdown("#### Lowest Energy Consumption Hours")
    st.dataframe(peak_hour.tail(5),use_container_width=True, hide_index=True)


# pictorially
daily_df = df.groupby('Date')[['Building Load (RT)', 'Chiller Energy Consumption (kWh)']].mean().round(2).reset_index()

st.markdown("<h3 style = 'text-align: center;'>Pictorial Demonstration</h3>", unsafe_allow_html=True)
col_ln, col_br = st.columns([4, 4], gap='medium', wrap=False)
with col_ln:
    fig, ax=plt.subplots(figsize=(10, 3))
    # building load plot
    ax.plot(daily_df['Date'], daily_df['Building Load (RT)'], linestyle='-', label= 'BL')
    # chiller energy consumption plot
    ax.plot(daily_df['Date'], daily_df['Chiller Energy Consumption (kWh)'], label='CEC', linestyle='-')
    plt.title('Building Load VS Chiller Energy Consumption')
    plt.xlabel('Date')
    plt.ylabel('BL/CEC')
    plt.grid(True)
    plt.legend()
    #plt.show()
    st.pyplot(fig)
with col_br:
    monthly_energy = df.groupby('Month')['Chiller Energy Consumption (kWh)'].sum().reset_index()
    plt.figure(figsize=(10,4))
    plt.bar(monthly_energy ['Month'], monthly_energy ['Chiller Energy Consumption (kWh)'])
    plt.title("Monthly Energy Consumption")
    plt.xlabel("Months")
    plt.ylabel("Energy Consumption")
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    #plt.show()
    st.pyplot(plt)
st.info("The system demonstrates high operational responsiveness, with energy consumption scaling predictably alongside building cooling demand across all operating seasons.")
st.markdown("----")

st.markdown("<h3 style = 'text-align: center;'>Factor Affecting Energy Consumption </h3>", unsafe_allow_html=True)
# corelation metrics
corre = df[['Chiller Energy Consumption (kWh)', 'Building Load (RT)', 'Outside Temperature (F)', 'Dew Point (F)', 'Humidity (%)', 'Cooling Water Temperature (C)']].corr().round(2)
# Apply a color gradient so positive numbers highlight in one color and negative in another
styled_corr = corre .style.background_gradient(
    cmap='coolwarm', axis=None, vmin=-1, vmax=1
).format("{:.2f}")
st.dataframe(styled_corr, use_container_width=True, hide_index=True)
st.info("Clearly we can see that, among all other factors, **Building Load** strongly co-relates with **Energy Consumption** (i.e the higher the building load the higher will be the energy consumption).")
st.markdown("----")
st.markdown("<h3 style = 'text-align: center;'>Coefficient of Performance </h3>", unsafe_allow_html=True)
st.info("To analyse HVAC system efficiency using Coefficient of Performance, we need to calculate system's cooling output relative to its electrical energy input.\n  The higher the COP, the lower will be the energy consumption, resulting the most efficient machine.")
df['COP'] = (df['Building Load (RT)'] * 3.517) / df['Chiller Energy Consumption (kWh)']
monthly_cop = df.groupby('Month')['COP'].mean().round(2).reset_index().sort_values(by = 'COP', ascending=False)
df['Month'] = df['Local Time (Timezone : GMT+8h)'].dt.month
monthly_cop_chrt = df.groupby('Month')['COP'].mean().reset_index().sort_values(by='Month')
hourly_cop = df.groupby('Hour')['COP'].mean().round(2).reset_index().sort_values(by = 'COP', ascending=False)
hourly_cop_chrt = df.groupby('Hour')['COP'].mean().reset_index()
col_ta, col_chr = st.columns([2,4], gap='medium', wrap=False)
with col_ta:
    st.markdown("#### Top Best Performing Hours")
    st.dataframe(hourly_cop.head(), use_container_width=True, hide_index=True)
with col_chr:
    fig, ax=plt.subplots(figsize=(10,4))
    ax.plot(hourly_cop_chrt['Hour'], hourly_cop_chrt['COP'], color='#2ca02c', linewidth = 2.5, label = 'Hourly Average COP')
    ax.set_title("System Hourly COP Trend")
    ax.set_xlabel('Hour')
    ax.set_ylabel('COP')
    #ax.legend(loc='upper right')
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    st.pyplot(fig)
# monthly performance
col_tab, col_chart = st.columns([2,4], gap='medium', wrap=False)
with col_tab:
    st.markdown("#### Top Best Performing Months")
    st.dataframe(monthly_cop.head(), use_container_width=True, hide_index=True)
with col_chart:
    fig, ax=plt.subplots(figsize=(10, 4))
    ax.plot(monthly_cop_chrt['Month'], monthly_cop_chrt['COP'], color='#2ca02c', linewidth = 2.5, label = 'Monthly Average COP')
    ax.set_title('System Monthly COP Trend')
    ax.set_xlabel("Month")
    ax.set_ylabel("COP")
    #ax.legend(loc = 'upper right')
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    st.pyplot(fig)
st.markdown("----")
# regression analysis
st.markdown("<h3 style = 'text-align: center;'>Regression Analysis </h3>", unsafe_allow_html=True)
reg_df = df[['Building Load (RT)', 'Chiller Energy Consumption (kWh)', 'Outside Temperature (F)', 'Humidity (%)', 'Cooling Water Temperature (C)']].dropna()
x = reg_df['Building Load (RT)']
y1 = reg_df['Chiller Energy Consumption (kWh)']
slope1, intercept1 = np.polyfit(x, y1,1)
y1_predict = slope1 * x + intercept1
corr_metrix = np.corrcoef(x,y1)
r_squared = corr_metrix[0, 1]**2
col_mets, col_rchart = st.columns([2,4], gap='medium', wrap=False)
with col_mets:
    st.metric('Regression Accuracy', f"{(r_squared)*100:.1f}%")
    st.metric("Prediction Farmula", f"E={slope1:.2f}*L+({intercept1:.2f})", delta=f'For every 1 RT increase, energy consumption increases by approximately **{slope1:.2f} kWh**.')
with col_rchart:
    fig, ax = plt.subplots(figsize=(10, 4))
    # scatter plot for actual data points
    ax.scatter(x, y1, color='#1f77b4', alpha=0.5, label='Actual Operating Data')
    # regression line for best fits
    ax.plot(x, y1_predict, color='red', linewidth=2.5, label=f'Regression Model: Energy = {slope1:.2f} * Load + {intercept1:.2f}')
    ax.set_title("Predictive Regression Analysis: Building Load VS Energy Consumption")
    ax.set_xlabel("Building Load")
    ax.set_ylabel('Energy Consumption')
    ax.legend(loc='upper left')
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    st.pyplot(fig)