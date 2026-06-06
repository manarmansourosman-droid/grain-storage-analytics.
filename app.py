import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px

# إعدادات الصفحة الخاصة بلوحة التحكم
st.set_page_config(page_title="Grain Storage Analytics", page_icon="🌾", layout="wide")

st.title("🌾 Grain Storage Monitoring & Analytics System")
st.markdown("### نظام التحليل الذكي ومراقبة المخزون - مشروع التخرج")
st.markdown("---")

# 1. توليد البيانات (Simulation)
@st.cache_data # عشان الكود ميعيدش التوليد مع كل ضغطة زرار
def generate_data():
    radius = 5
    height = 15
    np.random.seed(42)
    num_sensors = 200

    r = np.random.uniform(0, radius, num_sensors)
    theta = np.random.uniform(0, 2 * np.pi, num_sensors)
    x = r * np.cos(theta)
    y = r * np.sin(theta)
    z = np.random.uniform(0, height, num_sensors)

    temperature = np.random.uniform(12, 16, num_sensors)
    humidity = np.random.uniform(10, 13, num_sensors)

    df = pd.DataFrame({
        'Sensor_ID': [f'SNS_{i:03d}' for i in range(num_sensors)],
        'X': x, 'Y': y, 'Z': z,
        'Temperature': temperature, 'Humidity': humidity
    })

    # حقن النقطة الساخنة (Hot Spot)
    hot_spot_condition = (df['X']**2 + df['Y']**2 < 4) & (df['Z'] >= 6) & (df['Z'] <= 9)
    df.loc[hot_spot_condition, 'Temperature'] += np.random.uniform(6, 10, size=hot_spot_condition.sum())
    df.loc[hot_spot_condition, 'Humidity'] += np.random.uniform(3, 5, size=hot_spot_condition.sum())
    
    return df

df = generate_data()

# 2. خوارزمية الرصد والـ SPC
TEMP_THRESHOLD = 18.0
HUMID_THRESHOLD = 14.0

def classify_sensor(row):
    if row['Temperature'] > TEMP_THRESHOLD and row['Humidity'] > HUMID_THRESHOLD:
        return '🔴 High Risk (Hot Spot)'
    elif row['Temperature'] > TEMP_THRESHOLD or row['Humidity'] > HUMID_THRESHOLD:
        return '🟡 Warning (Sub-optimal)'
    else:
        return '🟢 Safe'

df['Alert_Level'] = df.apply(classify_sensor, axis=1)
df['Temp_Z_Score'] = (df['Temperature'] - df['Temperature'].mean()) / df['Temperature'].std()

# 3. عرض المؤشرات الرقمية (KPIs) في لوحة التحكم
counts = df['Alert_Level'].value_counts()
safe_count = counts.get('🟢 Safe', 0)
warning_count = counts.get('🟡 Warning (Sub-optimal)', 0)
risk_count = counts.get('🔴 High Risk (Hot Spot)', 0)

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(label="إجمالي عدد الحساسات", value=len(df))
with col2:
    st.metric(label="الحالة آمنة 🟢", value=safe_count)
with col3:
    st.metric(label="منطقة تحذير 🟡", value=warning_count)
with col4:
    st.metric(label="نقاط ساخنة حرجة 🔴", value=risk_count)

st.markdown("---")

# 4. تقسيم الشاشة لجزئين: الرسمة الـ 3D وجدول البيانات
left_col, right_col = st.columns([2, 1])

with left_col:
    st.subheader("📊 الخريطة الحرارية التفاعلية ثلاثية الأبعاد (3D Map)")
    fig = px.scatter_3d(
        df, x='X', y='Y', z='Z', color='Alert_Level',
        color_discrete_map={
            '🟢 Safe': 'green',
            '🟡 Warning (Sub-optimal)': 'orange',
            '🔴 High Risk (Hot Spot)': 'red'
        },
        hover_name='Sensor_ID',
        hover_data=['Temperature', 'Humidity', 'Temp_Z_Score']
    )
    fig.update_traces(marker=dict(size=5, opacity=0.8))
    fig.update_layout(
        scene=dict(xaxis_title='X', yaxis_title='Y', zaxis_title='Height (Z)',
                   xaxis=dict(range=[-6, 6]), yaxis=dict(range=[-6, 6]), zaxis=dict(range=[0, 16])),
        margin=dict(l=0, r=0, b=0, t=0)
    )
    st.plotly_chart(fig, use_container_width=True)

with right_col:
    st.subheader("🚨 الحساسات الحرجة المكتشفة")
    high_risk_df = df[df['Alert_Level'] == '🔴 High Risk (Hot Spot)'][['Sensor_ID', 'Temperature', 'Humidity', 'Temp_Z_Score']]
    if not high_risk_df.empty:
        st.dataframe(high_risk_df, use_container_width=True)
        st.error("⚠️ تنبيه: تم رصد بؤرة نشاط بيولوجي/حشري مرتفع في مركز الصومعة! يرجى تفعيل نظام التهوية.")
    else:
        st.success("✅ جميع أجزاء الصومعة مستقرة وتطابق معايير الـ FAO.")