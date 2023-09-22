import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import seaborn as sns
from scipy.stats import pearsonr

sns.set(style="dark")


def create_total_daily_rentals(df):
    """
    Create total daily rentals from a given DataFrame.

    Parameters:
    - df: The input DataFrame containing rental data.

    Returns:
    - daily_rentals: A DataFrame with total daily rentals, including the number of unique instances, the sum of rentals, and the count of rentals.
    """
    daily_rentals = df.resample(rule="D", on="dteday").agg(
        {"instant": "nunique", "cnt": ["sum", "count"]}
    )
    daily_rentals = daily_rentals.reset_index()

    return daily_rentals


def create_casual_daily_rentals(df):
    """
    Create casual daily rentals dataframe.

    Parameters:
    - df (pandas.DataFrame): The input dataframe containing rental data.

    Returns:
    - casual_rentals (pandas.DataFrame): The dataframe with daily casual rentals data.
    """
    casual_rentals = df.resample(rule="D", on="dteday").agg(
        {"instant": "nunique", "casual": ["sum", "count"]}
    )

    casual_rentals = casual_rentals.reset_index()

    return casual_rentals


def create_registered_daily_rentals(df):
    """
    Create registered daily rentals.

    Parameters:
    - df: DataFrame containing rental data.

    Returns:
    - register_rentals: DataFrame with aggregated registered daily rentals.
    """
    register_rentals = df.resample(rule="D", on="dteday").agg(
        {"instant": "nunique", "registered": ["sum", "count"]}
    )

    register_rentals = register_rentals.reset_index()

    return register_rentals


categorical_df = pd.read_csv("./dashboard/categorical_df.csv")
numerical_df = pd.read_csv("./dashboard/numerical_df.csv")

monthly_data = numerical_df.groupby("mnth").sum()["cnt"]

categorical_df["casual_percentage"] = categorical_df["casual"] / categorical_df["cnt"]
categorical_df["registered_percentage"] = (
    categorical_df["registered"] / categorical_df["cnt"]
)

categorical_df["dteday"] = pd.to_datetime(categorical_df["dteday"])

min_date = categorical_df["dteday"].min()
max_date = categorical_df["dteday"].max()

with st.sidebar:
    st.header("Portofolio Data Analysis Bike Rental")

    start_date, end_date = st.date_input(
        label="Period",
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date],
    )

    season = st.selectbox(
        label="Select the season",
        options=["All"] + list(categorical_df["season"].unique()),
    )

    weathersit = st.selectbox(
        label="Select the weather",
        options=["All"] + list(categorical_df["weathersit"].unique()),
    )

    if season == "All" and weathersit == "All":
        main_df = categorical_df[
            (categorical_df["dteday"] >= str(start_date))
            & (categorical_df["dteday"] <= str(end_date))
        ]
    elif season == "All":
        main_df = categorical_df[
            (categorical_df["dteday"] >= str(start_date))
            & (categorical_df["dteday"] <= str(end_date))
            & (categorical_df["weathersit"] == weathersit)
        ]
    elif weathersit == "All":
        main_df = categorical_df[
            (categorical_df["dteday"] >= str(start_date))
            & (categorical_df["dteday"] <= str(end_date))
            & (categorical_df["season"] == season)
        ]
    else:
        main_df = categorical_df[
            (categorical_df["dteday"] >= str(start_date))
            & (categorical_df["dteday"] <= str(end_date))
            & (categorical_df["season"] == season)
            & (categorical_df["weathersit"] == weathersit)
        ]

total_rentals = create_total_daily_rentals(main_df)
casual_rentals = create_casual_daily_rentals(main_df)
register_rentals = create_registered_daily_rentals(main_df)

total_rentals["total_diff"] = total_rentals["cnt"]["sum"].diff()
casual_rentals["casual_diff"] = casual_rentals["casual"]["sum"].diff()
register_rentals["register_diff"] = register_rentals["registered"]["sum"].diff()

with st.container():
    st.title("Bike Rentals Dashboard")
    st.divider()
    st.header("Pengenalan")
    st.markdown(
        """
        Kumpulan data tersebut memberikan informasi komprehensif tentang persewaan sepeda selama dua tahun (2011 dan 2012). Data dikategorikan berdasarkan berbagai faktor seperti waktu (tahun, bulan, hari), kondisi cuaca (suhu, kelembapan, kecepatan angin), dan jenis pengguna (biasa atau terdaftar). Laporan ini bertujuan untuk menganalisis data tersebut, dengan fokus khusus pada data harian, untuk mengidentifikasi pola dan korelasi yang dapat memberikan wawasan berharga bagi pengembangan bisnis.
        """
    )

    st.divider()

with st.container():
    st.header("Penyewaan Sepeda Harian")

    col1, col2, col3 = st.columns(3)

    with col1:
        sum_total_rentals = total_rentals["cnt", "sum"].sum()
        st.metric(
            label="Total Penyewaan",
            value=sum_total_rentals,
            delta=total_rentals["total_diff"].iloc[-1],
        )

    with col2:
        sum_casual_rentals = casual_rentals["casual", "sum"].sum()
        st.metric(
            label="Total Penyewaan Pengguna Biasa",
            value=sum_casual_rentals,
            delta=casual_rentals["casual_diff"].iloc[-1],
        )

    with col3:
        sum_register_rentals = register_rentals["registered", "sum"].sum()
        st.metric(
            label="Total Penyewaan Pengguna Terdaftar",
            value=sum_register_rentals,
            delta=register_rentals["register_diff"].iloc[-1],
        )

st.divider()

with st.container():
    st.header("Korelasi antar variabel")

    col1, col2 = st.columns(2)

    with col1:
        correlation_temp_hum, _ = pearsonr(main_df["temp"], main_df["hum"])
        st.metric(
            label="Korelasi antara suhu dan kelembapan",
            value=f"{correlation_temp_hum * 100:.2f}%",
        )
    with col2:
        correlation, _ = pearsonr(main_df["temp"], main_df["cnt"])
        st.metric(
            label="Korelasi antara suhu dan total keseluruhan sewa",
            value=f"{correlation * 100:.2f}%",
        )

st.divider()

with st.container():
    st.header(f"Total Penyewaan")

    st.line_chart(data=main_df, x="dteday", y="cnt")

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            label="Max Rentals",
            value=main_df["cnt"].max(),
        )
    with col2:
        st.metric(
            label="Min Rentals",
            value=main_df["cnt"].min(),
        )

st.divider()

with st.container():
    st.header("Total Penyewaan Pengguna Biasa")

    st.line_chart(data=main_df, x="dteday", y="casual")

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            label="Max Rentals",
            value=main_df["casual"].max(),
        )
    with col2:
        st.metric(
            label="Min Rentals",
            value=main_df["casual"].min(),
        )

st.divider()

with st.container():
    st.subheader("Total Penyewaan Pengguna Terdaftar")
    st.line_chart(data=main_df, x="dteday", y="registered")

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            label="Max Rentals",
            value=main_df["registered"].max(),
        )

    with col2:
        st.metric(
            label="Min Rentals",
            value=main_df["registered"].min(),
        )

st.divider()

with st.container():
    st.subheader("Tren Musiman")
    st.line_chart(data=monthly_data)

    cat_col_vis = ["season", "mnth"]

    fig, ax = plt.subplots(ncols=1, nrows=2, figsize=(15, 15))
    i = 0

    for cols in cat_col_vis:
        sns.barplot(
            x=categorical_df[cols],
            y=categorical_df["cnt"],
            ax=ax[i],
            edgecolor="#c5c6c7",
        )

        ax[i].set_xlabel(" ")
        ax[i].set_ylabel(" ")
        ax[i].xaxis.set_tick_params(labelsize=14)
        ax[i].tick_params(left=False, labelleft=False)
        ax[i].set_ylabel(cols, fontsize=16)
        ax[i].bar_label(ax[i].containers[0], size="12")
        i = i + 1

    st.pyplot(plt)

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            label="Max Rentals",
            value=monthly_data.max(),
        )

    with col2:
        st.metric(
            label="Min Rentals",
            value=monthly_data.min(),
        )

st.divider()

with st.container():
    st.subheader("Tren Suhu")
    st.line_chart(data=main_df, x="dteday", y="temp")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            label="Max Temperature",
            value=f"{(main_df['temp'].max() * 100):.2f}°C",
        )

    with col2:
        st.metric(
            label="Mean Temperature",
            value=f"{(main_df['temp'].mean() * 100):.2f}°C",
        )

    with col3:
        st.metric(
            label="Min Temperature",
            value=f"{(main_df['temp'].min() * 100):.2f}°C",
        )

with st.container():
    st.subheader("Tren Kelembapan")
    st.line_chart(data=main_df, x="dteday", y="hum")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(label="Max Humidity", value=f"{(main_df['hum'].max() * 100):.2f}%")

    with col2:
        st.metric(label="Mean Humidity", value=f"{(main_df['hum'].mean() * 100):.2f}%")

    with col3:
        st.metric(label="Min Humidity", value=f"{(main_df['hum'].min() * 100):.2f}%")

with st.container():
    st.subheader("Tren Kecepatan Angin")
    st.line_chart(data=main_df, x="dteday", y="windspeed")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            label="Max Windspeed",
            value=f"{(main_df['windspeed'].max() * 100):.2f} km/h",
        )

    with col2:
        st.metric(
            label="Mean Windspeed",
            value=f"{(main_df['windspeed'].mean() * 100):.2f} km/h",
        )

    with col3:
        st.metric(
            label="Min Windspeed",
            value=f"{(main_df['windspeed'].min() * 100):.2f} km/h",
        )

with st.container():
    st.subheader("Pengaruh Cuaca")

    plt.figure(figsize=(10, 5))
    sns.boxplot(x="weathersit", y="cnt", data=numerical_df)
    plt.title("Bike Rentals by Weather Situation")
    plt.xlabel("Weather Situation")
    plt.ylabel("Total Rentals")

    st.pyplot(plt)

with st.container():
    st.subheader("Pengaruh Pengguna")

    numerical_df["casual_percentage"] = numerical_df["casual"] / numerical_df["cnt"]
    numerical_df["registered_percentage"] = (
        numerical_df["registered"] / numerical_df["cnt"]
    )

    plt.figure(figsize=(10, 5))
    sns.lineplot(data=numerical_df, x="mnth", y="casual_percentage", label="Casual")
    sns.lineplot(
        data=numerical_df, x="mnth", y="registered_percentage", label="Registered"
    )
    plt.title("Casual vs Registered Users Over Time")
    plt.xlabel("Month")
    plt.ylabel("Percentage of Total Rentals")
    plt.legend()

    st.pyplot(plt)

with st.container():
    st.subheader("Kesimpulan")

    with st.expander(
        "Bagaimana perbedaan penyewaan sepeda pada musim dan bulan yang berbeda?"
    ):
        st.caption(
            """
            Tren ini menunjukkan bahwa cuaca dan suhu memainkan peranan penting dalam mempengaruhi pola penyewaan sepeda. Pada bulan-bulan dan musim-musim hangat cenderung terjadi peningkatan permintaan untuk persewaan sepeda, sedangkan pada periode-periode dingin terjadi penurunan permintaan.
            """
        )

    with st.expander("Bagaimana pengaruh cuaca terhadap persewaan sepeda?"):
        st.caption(
            """
            - Cerah, Sedikit awan, Berawan sebagian, Berawan sebagian (Situasi Cuaca 1): Ini adalah cuaca yang paling menguntungkan untuk persewaan sepeda dengan sekitar 7500 persewaan. Cuaca cerah atau berawan sebagian sangat ideal untuk aktivitas luar ruangan seperti bersepeda.

            - Kabut + Berawan, Kabut + Awan Pecah, Kabut + Sedikit Awan, Kabut (Situasi Cuaca 2): Situasi cuaca ini mengakibatkan penurunan jumlah penyewaan sepeda menjadi sekitar 5000. Kehadiran kabut atau awan pecah mungkin membuat bersepeda menjadi kurang menarik.

            - Salju Ringan, Hujan Ringan + Badai Petir + Awan Tersebar, Hujan Ringan + Awan Tersebar (Situasi Cuaca 3): Situasi cuaca ini memiliki kondisi yang paling tidak menguntungkan untuk bersepeda dengan sekitar 2500 persewaan. Cuaca buruk seperti hujan, salju, atau badai petir dapat membuat orang enggan melakukan aktivitas luar ruangan seperti bersepeda karena alasan keamanan dan ketidaknyamanan.
            """
        )

    with st.expander(
        "Apa perbedaan antara pengguna biasa dan pengguna yang terdaftar dalam hal pola penyewaan?"
    ):
        st.caption(
            """
            - Pengguna Biasa:

                Persentase total penyewaan oleh pengguna biasa lebih tinggi dibandingkan dengan pengguna terdaftar untuk semua bulan. Ada sedikit penurunan sekitar bulan ke-6, setelah itu meningkat lagi. Hal ini menunjukkan bahwa pengguna biasa mungkin lebih dipengaruhi oleh faktor-faktor seperti cuaca, hari libur, atau peristiwa yang terjadi pada waktu tersebut.

            - Pengguna Terdaftar:
            
                Persentase total penyewaan oleh pengguna terdaftar lebih rendah dibandingkan dengan pengguna biasa. Ada sedikit kenaikan sekitar bulan ke 6, setelah itu turun lagi. Hal ini dapat menunjukkan bahwa pengguna terdaftar memiliki pola penggunaan yang lebih konsisten sepanjang tahun, namun mungkin ada waktu tertentu (misalnya bulan ke-6) ketika penggunaan mereka meningkat.
            """
        )

    with st.expander("Apakah ada korelasi antara kondisi cuaca dan penyewaan sepeda?"):
        st.caption(
            """
            Tampaknya ada korelasi yang kuat antara kondisi cuaca dan penyewaan sepeda, dengan cuaca cerah atau berawan sebagian menjadi pilihan yang paling menguntungkan bagi persewaan sepeda, dan kondisi cuaca buruk seperti salju ringan atau hujan menjadi yang paling tidak menguntungkan.
            """
        )

    with st.expander(
        "Bagaimana pengaruh waktu dalam setahun terhadap perilaku pengguna biasa versus pengguna terdaftar?"
    ):
        st.caption(
            """
            Tampaknya baik pengguna yang terdaftar maupun pengguna biasa lebih memilih untuk menyewa sepeda dalam kondisi cuaca cerah atau sebagian berawan sepanjang musim. Namun, pengguna yang terdaftar tampaknya lebih toleran terhadap kondisi cuaca buruk dibandingkan pengguna biasa. Informasi ini dapat berguna untuk memprediksi pola persewaan sepeda dan menginformasikan strategi pemasaran. Misalnya, promosi tambahan dapat direncanakan pada saat cuaca diperkirakan cerah atau berawan sebagian, sehingga dapat meningkatkan harga sewa di kalangan pengguna biasa. Sebaliknya, strategi dapat dikembangkan untuk mendorong penyewaan sepeda di kalangan pengguna biasa selama kondisi cuaca buruk.
            """
        )

    with st.expander(
        "Bagaimana kita bisa mengoptimalkan ketersediaan sepeda sesuai tren musiman?"
    ):
        st.caption(
            """
            - Meningkatkan Ketersediaan Selama Musim Puncak:
            
                Data menunjukkan bahwa puncak persewaan sepeda terjadi pada musim panas dan musim gugur. Oleh karena itu, akan bermanfaat untuk meningkatkan ketersediaan sepeda selama bulan-bulan ini untuk memenuhi tingginya permintaan.
            
            - Perawatan dan Perbaikan Selama Musim Off-Peak:
                
                Musim dingin dan musim semi menunjukkan permintaan persewaan sepeda yang lebih rendah. Ini adalah saat yang tepat untuk menjadwalkan perawatan dan perbaikan rutin untuk memastikan sepeda berada dalam kondisi optimal untuk musim puncak.

            - Aktivitas promosi:
                        
                Untuk mendorong penyewaan sepeda selama musim sepi atau bulan-bulan dengan permintaan lebih rendah, kegiatan promosi seperti diskon atau program loyalitas dapat diperkenalkan.

            - Penggunaan Alternatif:
                
                Selama musim dingin ketika permintaan rendah, pertimbangkan penggunaan alternatif sepeda. Misalnya, mereka dapat disewakan untuk jangka waktu yang lebih lama atau digunakan dalam kemitraan dengan operator tur lokal untuk tur berpemandu.

            - Harga Dinamis:
                
                Menerapkan model penetapan harga dinamis di mana harga lebih rendah selama musim sepi untuk mendorong penggunaan, dan lebih tinggi selama musim puncak ketika permintaan tinggi.

            - Sepeda Tahan Cuaca:
                
                Pertimbangkan untuk berinvestasi pada sepeda tahan cuaca atau menyediakan perlengkapan tambahan seperti penutup hujan atau perlengkapan penghangat selama musim dingin untuk menarik pelanggan.
            """
        )

    with st.expander(
        "Bisakah kita memperkirakan permintaan sewa sepeda berdasarkan kondisi cuaca?"
    ):
        st.caption(
            """
            Ya, permintaan persewaan sepeda dapat diprediksi berdasarkan kondisi cuaca menggunakan model pembelajaran mesin. Kondisi cuaca seperti suhu, kelembapan, kecepatan angin, dan situasi cuaca (cerah, mendung, hujan, dll) dapat mempengaruhi permintaan sewa sepeda secara signifikan.

    Berdasarkan grafik yang Anda berikan, kami dapat melihat dengan jelas tren persewaan sepeda dalam berbagai situasi cuaca. Misalnya, Situasi Cuaca 1 (Cerah, Sedikit awan, Berawan sebagian) memiliki jumlah rental tertinggi, diikuti oleh Situasi Cuaca 2 (Kabut + Berawan, Kabut + Awan pecah, Kabut + Sedikit awan), dan kemudian Situasi Cuaca 3 (Cerah Salju, Hujan Ringan + Badai Petir + Awan berserakan). Hal ini menunjukkan bahwa cuaca cerah atau berawan sebagian paling menguntungkan bagi persewaan sepeda, sedangkan cuaca buruk seperti hujan atau salju mengurangi permintaan.

    Tren ini dapat digunakan untuk melatih model pembelajaran mesin guna memprediksi permintaan sewa sepeda berdasarkan kondisi cuaca. Model tersebut dapat mengambil data cuaca sebagai masukan dan keluaran perkiraan jumlah penyewaan sepeda. Hal ini khususnya berguna untuk perencanaan dan alokasi sumber daya dalam layanan penyewaan sepeda.
            """
        )
