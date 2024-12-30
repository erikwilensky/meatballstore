import matplotlib.pyplot as plt
import streamlit as st

def generate_profit_pie_chart(barber_profit, shoe_profit, meatball_profit):
    """
    Generate and display a pie chart for profit breakdown with absolute values.
    """
    labels = ['Barber Shop', 'Shoe Shop', 'Meatball Stand']
    sizes = [barber_profit, shoe_profit, meatball_profit]
    colors = ['#ff9999', '#66b3ff', '#99ff99']
    explode = (0.1, 0, 0)  # explode the first slice

    fig, ax = plt.subplots()
    wedges, texts, autotexts = ax.pie(
        sizes, explode=explode, labels=labels, colors=colors,
        autopct=lambda p: f'{int(p * sum(sizes) / 100):,} ฿', startangle=90
    )
    ax.axis('equal')  # Equal aspect ratio ensures the pie is drawn as a circle.

    # Customizing the text
    for text in texts:
        text.set_fontsize(12)
    for autotext in autotexts:
        autotext.set_fontsize(12)

    st.pyplot(fig)

def generate_profit_line_chart(data, start_date, end_date):
    """
    Generate and display a line chart for profit over time.
    """
    fig, ax = plt.subplots()

    for shop, profits in data.items():
        dates = list(profits.keys())
        values = list(profits.values())
        ax.plot(dates, values, label=shop)

    ax.set_title(f"Profit Trends ({start_date} to {end_date})")
    ax.set_xlabel("Date")
    ax.set_ylabel("Profit (฿)")
    ax.legend()
    st.pyplot(fig)
