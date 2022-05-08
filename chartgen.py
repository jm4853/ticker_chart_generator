import yfinance
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from tkinter import *
from PIL import Image, ImageTk

# Delcare global array that is populated later
fields = {}

def validateTicker(fields):
     # Makes a call to the yfinance api, receiving a pandas dataframe
    stock = yfinance.Ticker(fields["ticker"].get())
    if (stock.info['regularMarketPrice'] == None):
        # The API call is bandwidth intensive, so instead of making another
        # call in a seperate function, this function returns a tuple containing
        # both the result and the pandas dataframe
        return (False, stock)
    return (True, stock)


def makeAndPrintChart():
    global fields
    # validateTicker returns a tuple with a boolean value and the stock
    # object. This is because the way it validates is by getting the stock
    # data, and it would require another api call to get the stock again
    # if it was not returned
    stockExists, stock = validateTicker(fields)
    if stockExists:
        chart = makeChart(fields, stock)
        chart.write_image("stock.png")
        fields["chart"].changePic()
    else:
        fields["text"].config(text="Invalid Ticker")
    
    
def makeChart(fields, stock):
    stockName = fields["ticker"].get()
    period = fields["period"].get()
    rollingAvg = fields["avg"].get()
    
    
    hist = stock.history(period=period)
    hist['diff'] = hist['Close'] - hist['Open']
    hist.loc[hist['diff']>=0, 'color'] = 'green'
    hist.loc[hist['diff']<0, 'color'] = 'red'
    
    
    chart = make_subplots(specs=[[{"secondary_y": True}]])
    chart.add_trace(go.Candlestick(x=hist.index,
                                  open=hist['Open'],
                                  high=hist['High'],
                                  low=hist['Low'],
                                  close=hist['Close'],
                                  name="Price"))
    # Rolling value must be in terms of the period the user entered
    chart.add_trace(go.Scatter(x=hist.index,y=hist['Close'].rolling(window=20).mean(),marker_color='blue',name=f'{rollingAvg} Day MA'))
    chart.add_trace(go.Bar(x=hist.index, y=hist['Volume'], name='Volume', marker={'color':hist['color']}), secondary_y=True)
    
    # Sets range of y axis for volume to 4 times the max value, that way it takes up
    # about a quarter of the screen
    chart.update_yaxes(range=[0, hist['Volume'].max() * 4], secondary_y=True)
    chart.update_yaxes(visible=False, secondary_y=True)
    chart.update_layout(xaxis_rangeslider_visible=False)
    return chart
    



def initFields(window):    
    Button(window, text="Quit", font=("Arial", 10), command=window.destroy, ).place(relx=1, rely=0, anchor=NE)

    tickerEntry = Entry(window, width = 12)
    tickerEntry.insert(0, 'Stock Ticker')
    tickerEntry.grid(column=0, row=0)



    # 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
    periodList = ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max']
    periodVar = StringVar()
    periodVar.set("Period")
    periodSelect = OptionMenu(window, periodVar, *periodList)
    periodSelect.grid(column=0, row=1)


    tkInt = IntVar()
    avgScale = Scale(window, variable=tkInt, from_=7, to=90, orient=HORIZONTAL)
    avgScale.grid(column=0, row=3)
    avgLabel = Label(window, text = "Rolling Day Average:", font=("Arial", 10))
    avgLabel.grid(column=0, row=2)



    startButt = Button(window, text="Create", command=makeAndPrintChart, font=("Arial", 10))
    startButt.grid(column=0, row=4)
    
    userText = Label(window, text="", font=("Arial", 10))
    userText.grid(column=0, row=5)
    
    
    fields = {
        "ticker": tickerEntry,
        "period": periodVar,
        "avg": avgScale,
        "text": userText,
        }
    return fields


class Picture:
    def __init__(self, window):
        self.window = window
        self.img = Image.open("welcome.png")
        
        self.img = ImageTk.PhotoImage(self.img)
        
        self.label = Label(window, image=self.img)
        self.label.grid(column=2, row=0, rowspan=20)
    
    def changePic(self):
        self.img = Image.open("stock.png")
        self.img = self.img.crop((50, 100, 700, 450))
        self.img = self.img.resize((650, 400), Image.ANTIALIAS)
        
        self.img = ImageTk.PhotoImage(self.img)
        
        self.label.config(image=self.img)



window = Tk()

window.title("Chart Generator")
window.geometry("800x400")

# Creates actual frame, happens normally
# inside mainLoop()
app = Frame(window)
app.grid()


pic = Picture(window)
fields = initFields(window)
fields["chart"] = pic


window.mainloop()

print("closed")