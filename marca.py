import geopandas as gpd
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from selenium import webdriver
import textwrap
import time

# Load website
driver = webdriver.Chrome()
driver.get('https://www.marca.com/futbol/top-100.html')

# Manage cookies
time.sleep(1)
configuration_button = driver.find_element('xpath', '//*[@id="didomi-notice-learn-more-button"]')
configuration_button.click()
time.sleep(1)
disagree_to_all_button = driver.find_element('xpath', '//*[@id="didomi-consent-popup"]/div/div/div/div/div[4]/div/button[1]')
disagree_to_all_button.click()

# Get players' info
players = driver.find_elements('class name', 'contenedorEscudo')
player_info = []
for player in players:
    time.sleep(0.1)
    player.click()
    name = driver.find_element('xpath', '//*[@id="nombre"]').text
    team = driver.find_element('xpath', '//*[@id="equipo"]').text
    league = driver.find_element('xpath', '//*[@id="liga"]').text
    nationality = driver.find_element('xpath', '//*[@id="pais"]').text
    age = driver.find_element('xpath', '//*[@id="edad"]').text
    position = driver.find_element('xpath', '//*[@id="demarcacion"]').text

    player_dict = {
        'Name': name,
        'Nationality': nationality,
        'Team': team,
        'League': league,        
        'Age': age[:2],
        'Position': position
    }
    player_info.append(player_dict)

# Create dataframe and translate positions
df = pd.DataFrame.from_dict(player_info)

position_replace_values = {
    'ATACANTE': 'FOR',
    'CENTROCAMPISTA': 'MID',
    'DEFENSA': 'DEF',
    'PORTERO': 'GK'
}
df = df.replace({'Position': position_replace_values})

# Create values to plot
nationality_count = df['Nationality'].value_counts()
team_count = pd.DataFrame(df['Team'].value_counts())
league_count = pd.DataFrame(df['League'].value_counts())
position_count = df['Position'].value_counts()
age_count = pd.DataFrame(df['Age'].value_counts())
age_count.sort_index(inplace=True)

# Get shp files
shape_file_path = 'Paises_Mundo/Paises_Mundo.shp'
"Shape downloaded from http://www.efrainmaps.es. Carlos Efraín Porto Tapiquén. Geografía, SIG y Cartografía Digital. Valencia, Spain, 2020."
shape_df = gpd.read_file(shape_file_path)

# Remove Antarctica
shape_df = shape_df.drop(14)

# Join the count dataframe and the shape dataframe
nationality_count.index = [country_name.lower() for country_name in nationality_count.index]
shape_df['PAÍS'] = [country_name.lower() for country_name in shape_df['PAÍS']]
map_df = shape_df.set_index('PAÍS').join(nationality_count)

# Create figure
fig = plt.figure(
    figsize=(10,16),
    facecolor='#eeeeee'
)
# Add title
fig.suptitle(
    'Los 100 de MARCA (2022-2023)',
    color='#141E61',
    fontsize=20
)

#Set style
sns.set_style('darkgrid')
sns.set_context(
    rc = {
        'patch.linewidth': 0.0
    }
)

# Create axis
# Countries ax
plot1 = plt.subplot2grid(
    (4, 2),
    (0, 0),
    colspan=2
)
# Teams ax
plot2 = plt.subplot2grid(
    (4, 2),
    (1, 0),
    rowspan=2
)
# Leagues ax
plot3 = plt.subplot2grid(
    (4, 2),
    (1, 1),
    rowspan=2
)
# Ages ax
plot4 = plt.subplot2grid(
    (4, 2),
    (3, 0)
)
# Positions ax
plot5 = plt.subplot2grid(
    (4, 2),
    (3, 1)
)

# Create plots
# Countries plot
boundary_ax = map_df.boundary.plot(
    ax=plot1,
    edgecolor='black',
    linewidth=0.1,
)
map_df.plot(
    ax=boundary_ax,
    column='Nationality',
    legend=True,
    cmap='winter',
    legend_kwds={
        'shrink': 0.6
    }
)
# Teams plot
sns.barplot(
    x='Team',
    y=team_count.index,
    data=team_count,
    ax=plot2,
    color='#0F044C'
)
# Leagues plot
sns.barplot(
    x='League',
    y=league_count.index,
    data=league_count,
    ax=plot3,
    color='#0F044C'
)
# Ages plot
sns.barplot(
    x=age_count.index,
    y='Age',
    data=age_count,
    ax=plot4,
    color='#0F044C'
)
# Positions plot
patches, texts, autotexts = plot5.pie(
    position_count,
    labels=position_count.index,
    colors=sns.blend_palette(
        [
            '#787A91',
            '#0F044C'
        ],
        len(position_count)
    ),
    autopct='%.0f%%'
)

# Modify text in pie plot
for text in texts:
    text.set_color('#141E61')
for autotext in autotexts:
    autotext.set_color('#eeeeee')
    autotext.set_fontweight('bold')

# Wrap labels in league bar plot
wrapped_labels = []
for label in plot3.get_yticklabels():
    text = label.get_text()
    wrapped_labels.append(
        textwrap.fill(
            text,
            width=8,
            break_long_words=False
        )
    )

# Modify style in plots
for title, ax in zip(df.columns[1:], fig.axes):
    ax.set_title(
        label=title,
        color='#141E61',
        fontweight='bold'
    )
    ax.set_facecolor('#787A91')
    ax.tick_params(
        axis='x',
        colors='#141E61'
    )
    ax.tick_params(
        axis='y',
        colors='#141E61'
    )
    ax.set(
        xlabel=None,
        ylabel=None
    )
    if ax.title.get_text() == 'Nationality':
        ax.axis('off')
    if ax.title.get_text() == 'Teams':
        ax.tick_params(
            axis='y',
            labelsize=8
        )
    if ax.title.get_text() == 'Leagues':
        ax.set_yticklabels(
            wrapped_labels,
            fontsize=7
        )

# Add footnote
plt.figtext(
    0.9,
    0,
    'Fuente: Marca.com',
    color='#141E61',
    fontsize=7
)

plt.tight_layout()
plt.show()