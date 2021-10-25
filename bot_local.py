# SETUP: VIRTUAL ENVIRONMENT
## for environment variables
from dotenv import load_dotenv
import os

## for chatbot functionalities
import telebot
from string import Template
import emoji
from gtts import gTTS

## for data analysis
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

# SETUP: TELEGRAM BOT API TOKEN
load_dotenv()
TOKEN = os.environ['TOKEN']
bot = telebot.TeleBot(TOKEN)


# -------------------- CHECKPOINT 1 --------------------
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    # TO DO: chat_id, full_name, message_text
    chat_id = message.from_user.id

    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    full_name = f'{first_name} {last_name}' if last_name is not None else first_name
    
    # TO DO: subtitute text with variable
    with open('template_text/welcome.txt', mode='r', encoding='utf-8') as f:
        content = f.read()
        temp = Template(content)
        welcome = temp.substitute(FULL_NAME = full_name)

    bot.send_message(
        chat_id,
        welcome,
        parse_mode='Markdown'
    )

@bot.message_handler(commands=['about'])
def send_about(message):
    # TO DO: chat_id
    chat_id = message.from_user.id

    # TO DO: subtitute text with static values
    with open('template_text/about.txt', mode='r', encoding='utf-8') as f:
        content = f.read()
        temp = Template(content)
        about = temp.substitute(
            STUDENT_NAME = "MOCHAMMAD MAULANA YUSUF",
            BATCH_ACADEMY = "PHOENIX",
            GITHUB_REPO_LINK = "https://github.com/mochammadmaulanay/capstone_da_phoenix_Telegram-Chatbot"
        )

    bot.send_message(
        chat_id,
        about,
        parse_mode='Markdown'
    )


# -------------------- CHECKPOINT 2 --------------------
# TO DO: get unique values of campaign_id
df = pd.read_csv('data_input/facebook_ads_v2.csv', parse_dates=['reporting_date'])

# TO DO: get unique values of campaign_id
df['campaign_id'] = df['campaign_id'].astype('str')
unique_campaign = df['campaign_id'].unique()

@bot.message_handler(commands=['summary'])
def ask_id_summary(message):
    # TO DO: chat_id (SAME AS CHECKPOINT 1)
    chat_id = message.from_user.id

    markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
    for i in unique_campaign:
        markup.add(i)
    sent = bot.send_message(chat_id, 'Choose campaign to be summarized:', reply_markup=markup)

    bot.register_next_step_handler(sent, send_summary)

def send_summary(message):
    # TO DO: chat_id (SAME AS CHECKPOINT 1)
    chat_id = message.from_user.id
    selected_campaign_id = message.text

    if selected_campaign_id in unique_campaign:
        # TO DO: find the range date
        df_campaign = df[df['campaign_id']==selected_campaign_id]
        
        start_date = df_campaign['reporting_date'].min().strftime(format='%d %b %Y')
        end_date = df_campaign['reporting_date'].max().strftime(format='%d %b %Y')
        
        # TO DO: perform calculation
        total_spent = int(df_campaign['spent'].sum())
        total_conversion = int(df_campaign['total_conversion'].sum())
        cpc = round(total_spent / total_conversion,1)

        # TO DO: subtitute text with variables
        with open('template_text/summary.txt', mode='r', encoding='utf-8') as f:
            content = f.read()
            temp = Template(content)
            summary = temp.substitute(
                CAMPAIGN_ID = selected_campaign_id,
                START_DATE = start_date,
                END_DATE = end_date,
                TOTAL_SPENT = f"${total_spent:,.0f}",
                TOTAL_CONVERSION = f"{total_conversion:,.0f}",
                CPC = f"${cpc:,.1f}"
            )

        bot.send_message(chat_id, summary)
    else:
        bot.send_message(chat_id, 'Campaign ID not found. Please try again!')
        ask_id_summary(message)


# # -------------------- CHECKPOINT 3 --------------------
@bot.message_handler(commands=['plot'])
def ask_id_plot(message):
#     # TO DO: chat_id (SAME AS CHECKPOINT 1)
    chat_id = message.from_user.id

    markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
    for i in unique_campaign:
        markup.add(i)
    sent = bot.send_message(chat_id, 'Choose campaign to be visualized:', reply_markup=markup)

    bot.register_next_step_handler(sent, send_plot)

def send_plot(message):
    # TO DO: chat_id (SAME AS CHECKPOINT 1)
    chat_id = message.from_user.id
    selected_campaign_id = message.text

    if selected_campaign_id in unique_campaign:
        # TO DO: prepare data for visualization
        df_campaign = df[df['campaign_id']==selected_campaign_id]
        df_plot = df_campaign.groupby('age').agg({'spent':'sum','approved_conversion':'sum'})
        df_plot['cpc'] = df_plot['spent'] / df_plot['approved_conversion']
        
        # TO DO: visualization

        # prepare 3 subplots vertically
        fig, axes = plt.subplots(3, sharex=True, dpi=300)

        # create frameless plot
        for ax in axes:
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_visible(False)
            ax.spines['bottom'].set_visible(False)

        # first subplot: total spent per age group
        axes[0].bar(x=df_plot.index, height=df_plot['spent'], color='#AE2024')
        axes[0].set_ylabel('Total Spent', fontsize=8)

        # second subplot: total approved conversion per age group
        axes[1].bar(x=df_plot.index, height=df_plot['approved_conversion'], color='#000000')
        axes[1].set_ylabel('Total Approved\nConversion', fontsize=8)

        # third subplot: average CPC per age group
        axes[2].bar(x=df_plot.index, height=df_plot['cpc'], color='#AE2024')
        axes[2].set_ylabel('Average CPC', fontsize=8)

        # set the label and title for plots
        plt.xlabel('Age Group')
        axes[0].set_title(
            f'''Average CPC, Total Spent, and Total Approved Conversion
            across Age Group for Campaign ID: {selected_campaign_id}''')

        # create output folder
        if not os.path.exists('output'):
            os.makedirs('output')

        # save plot
        plt.savefig('output/plot.png', bbox_inches='tight')

        # send plot
        bot.send_chat_action(chat_id, 'upload_photo')
        with open('output/plot.png', 'rb') as img:
            bot.send_photo(chat_id, img)

        # (EXTRA CHALLENGE) Voice Message
        plot_info = list(zip(
            ['total spent','total approved conversion','average CPC'],
            df_plot.idxmax(),
            df_plot.idxmin()))

        plot_text = f'This is your requested plot for Campaign Id {selected_campaign_id}.\n'
        for col, maxi, mini in plot_info:
            text = f"Age group with the highest {col} is {maxi}, while the lowest is {mini}.\n"
            plot_text += text

        # save voice message
        speech = gTTS(text = plot_text)
        speech.save('output/plot_info.ogg')

        # send voice message
        with open('output/plot_info.ogg', 'rb') as f:
            bot.send_voice(chat_id, f)
    else:
        bot.send_message(chat_id, 'Campaign ID not found. Please try again!')
        ask_id_plot(message)


# -------------------- CHECKPOINT 4 --------------------
@bot.message_handler(func=lambda message: True)
def echo_all(message):
    # TO DO: emoji
    with open('template_text/default.txt', mode='r', encoding='utf-8') as f:
        temp = Template(f.read())
        default = temp.substitute(EMOJI = emoji.emojize(':frowning_face:'))
        
    bot.reply_to(message, default)
if __name__ == "__main__":
    bot.polling()