"""
Imports

"""

import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askopenfilename
from tkinter import messagebox
import pandas as pd
import os
import time
import json
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
import seaborn as sns

"""
Phase - I Data Import & Translate
"""


# Python Class to convert imported csv data to json file and store in filesystem
class ConvertToJson:
    # Input for function : CSV File name
    # Class Method for conversion and storage
    def csv_to_json(self, filename):
        # Trim only the file name - Removes path and file extension
        head, tail = os.path.split(filename)
        header = tail[:-4]
        json_file_name = head + '/' + header + ".json"
        json_create_time = time.time()
        print("File Conversion from csv to Json")
        print(f"Reading file => {filename}")

        # Call to function - Read CSV which uses to pandas to read csv and store as data-frame
        # It also checks if the file imported includes 'PROGRAM STATUS' and filters 'ACTIVE' rows
        active_view = read_csv()

        # Use of Pandas to convert data-frame to json string
        result = active_view.to_json(orient='split')
        # Use of python's json constructs to deserialise the 'result' variable
        parsed = json.loads(result)

        # Check for old file with same name. If found, delete. Avoid any potential file corruption
        if os.path.exists(json_file_name):
            os.remove(json_file_name)
            print("Existing File Removed. Creation of New File")
            print(f"Writing to file => {json_file_name}")

        # Json File Creation
        with open(json_file_name, 'w') as jsoninspec:
            jsoninspec.write(json.dumps(parsed, sort_keys=True, indent=4))

        # Out with time taken
        print(f"--- JSON File Creation completed in {round(time.time() - json_create_time, 3)} seconds ---")
        # Close file
        jsoninspec.close()

        print("=" * 10 + " SUCCESS " + "=" * 10)
        print("CSV to JSON Operation Completed")
        print("Your File is placed in - ")
        print(json_file_name)

        return json_file_name


# Function to read the CSV and convert to a dataframe
def read_csv():
    try:
        # Read CSV using pandas
        csv_df = pd.read_csv(csv_file_path, dtype=object)

    except UnboundLocalError:
        print("UnboundLocalError: Please Enter a Valid CSV file & try")

    except ValueError:
        print("Unable to Open/Load Your File. Try Again!")

    except AttributeError:
        print("Unable to Open/Load Your File. Try Again!")

    # To Allow only ACTIVE - PROGRAM STATUS to be displayed
    try:
        active_view = csv_df[csv_df['PROGRAM STATUS'].str.contains("^ACTIVE")]

    except UnboundLocalError:
        print("UnboundLocalError: Please Enter a Valid CSV file & try")
        tk.messagebox.showinfo('File Import - Unsuccessful',
                               message=f'Please use a proper CSV & Try')

    # No Action required if file does not include ACTIVE Program Status
    except KeyError:
        active_view = csv_df

    # return the active_view dataframe
    return active_view


# Function to load imported CSV for further processing under 'Data Import & Translate' Module
def import_csv_data(tree_input):
    global csv_file_path, json_file_name

    # To ensure only CSV files are selected to Import CSV
    csv_file_path = askopenfilename(title='Open CSV File', filetypes=(('CSV Files', '*.csv'),))
    csv_import_time = time.time()
    if csv_file_path:

        # Clean up csv path
        csv_file_path = r"{}".format(csv_file_path)

        # Data type set as object to prevent conversion of int to float
        active_view = read_csv()

        # Clear Old Tree View
        clear_tree()

        if tree_input == 'my_tree':
            print(f"--- CSV Import completed in {round(time.time() - csv_import_time, 3)} seconds ---")
            print("Setting Up your Treeview")
            treeview_time = time.time()
            # Setup New Tree
            my_tree["column"] = list(active_view.columns)
            my_tree["show"] = "headings"

            # Loop Through for handling the headers
            for column in my_tree["column"]:
                my_tree.heading(column, text=column)

            # Put Data in Tree-view
            df_rows = active_view.to_numpy().tolist()
            for row in df_rows:
                my_tree.insert("", "end", values=row)
            print(f"--- Tree-view processing completed in {round(time.time() - treeview_time, 3)} seconds ---")
    else:
        # If the user click cancel on the file selection dialogue box
        pass


def csv_frame_format():
    import_csv_data('my_tree')
    if csv_file_path:
        my_frame.pack(before=import_csv_btn, fill='both', expand=1)
        my_tree.pack(fill='both', expand=1)
        tree_vscroll_bar.config(command=my_tree.yview)
        tree_hscroll_bar.config(command=my_tree.xview)

        new_label.config(text='Imported CSV Results. JSON File Created Successfully')

        # Object Creation of ConvertToJson Class
        inspection = ConvertToJson()
        json_file_name = inspection.csv_to_json(csv_file_path)
        tk.messagebox.showinfo('JSON Convert Success', message=f'JSON File Path: \n {json_file_name}')


"""
Phase II - Data Clean & Calculate
"""


def import_json_data():
    global csv_file_path, json_file_path

    # To ensure only JSON files are selected to Import JSON
    json_file_path = askopenfilename(title='Open JSON File', filetypes=(('JSON Files', '*.json'),))
    print("Starting with your JSON Data Clean - Please Wait!")
    json_import_time = time.time()

    if json_file_path:
        try:
            json_file_path = r"{}".format(json_file_path)

            # Data read JSON File & Convert to store as Data-frame
            json_df = pd.read_json(json_file_path, orient='split')
            print("JSON Data Clean - In-Progress")
        except UnboundLocalError:
            print("UnboundLocalError: Please Enter a Valid JSON file & try")

        except ValueError:
            print("Unable to Open/Load Your File. Try Again!")

        # Data Cleaning RegEx patterns to exclude some unwanted characters/text/numbers
        try:
            json_df.dropna(how='all')
            for column in json_df.columns:
                # Remove comma from the thousands numbers (1-1,999 => 1-1999)
                json_df[column] = json_df[column].astype(str).str.replace(r'(\,)', "")
                # Remove whitespace at begining of string
                json_df[column] = json_df[column].astype(str).str.replace(r'^(\s)', "")
                # For consistency SF & SQ.FT within PE DESCRIPTION, having standard as SF
                json_df[column] = json_df[column].astype(str).str.replace(r'\s[A-Z]\D\W\D\D\D\W', " SF")
                # To remove double whitespace. THE CAFE  AT => THE CAFE AT
                json_df[column] = json_df[column].astype(str).str.replace(r'[\s][\s]', " ")
                json_df[column] = json_df[column].astype(str).str.replace(r'(\s)[)]', ")")
                # SANTA&#160;MONICA => SANTA MONICA
                json_df[column] = json_df[column].astype(str).str.replace(r'([|\^&+\%*\=#;!>]+\d+\W)', " ")
                # 1100 N WESTERN AVE # #101 => 1100 N WESTERN AVE # 101
                json_df[column] = json_df[column].astype(str).str.replace(r'(# #)', "# ")
                # Remove extra space after $ at begining of string
                json_df[column] = json_df[column].astype(str).str.replace(r'^(\$ )', "$")
                # Remove unwanted $ with space symbols
                json_df[column] = json_df[column].astype(str).str.replace(r'(\$ )', " ")

            try:
                # Extraction of VENUE (Seats/SquareFeet) CAPACITY in to a new Column
                # Regex - Data pattern to extract the VENUE CAPACITY values from PE DESCRIPTION column
                data_pattern = r'([0-9]+-+.[0-9]+|[0-9]+-\d{4}' \
                               r'|[0-9]\d{3}-[0-9]\d{3}' \
                               r'|[0-9]+-+.[0-9]+\s[A-Z]+' \
                               r'|\d{4}\W+\s[A-Z]+|[0-9]+\W\s[A-Z]+|[0-9]+\s\W)'
                json_df['VENUE CAPACITY'] = json_df['PE DESCRIPTION'].astype(str).str.extract(data_pattern)
                json_df['PE DESCRIPTION'] = json_df['PE DESCRIPTION'].astype(str).str.replace(
                    "\(" + data_pattern + "\)", "")
                json_df.inplace = True
                print("JSON Data Clean - Almost Done!")

            except KeyError:
                print("'PE DESCRIPTION' column not found, Moving On to next stage")
                pass
        except:
            pass

        print(f"--- JSON Import - Post Data Clean completed in {round(time.time() - json_import_time, 3)} seconds ---")
        print("Setting Up your Tree-view")
        clear_tree()
        treeview_time = time.time()
        # Setup New Tree
        my_tree1["column"] = list(json_df.columns)
        my_tree1["show"] = "headings"
        # Loop Through for handling the headers
        for column in my_tree1["column"]:
            my_tree1.heading(column, text=column)

        # Put Data in Tree-view
        df_rows = json_df.to_numpy().tolist()
        for row in df_rows:
            my_tree1.insert("", "end", values=row)

        print(f"--- Tree-view processing completed in {time.time() - treeview_time:.3f} seconds ---")
        return json_df


def json_data_clean():
    out_df = import_json_data()

    if json_file_path:
        my_frame.pack(before=import_csv_btn, fill='both', expand=1)
        my_tree.pack(fill='both', expand=1)
        tree_vscroll_bar.config(command=my_tree.yview)
        tree_hscroll_bar.config(command=my_tree.xview)

        # Updating the label to update the user on operation updates
        new_label.config(text='Imported JSON Results. Choose Option from Below')

        my_frame1.pack(before=import_json_btn1, fill='both', expand=1)
        my_tree1.pack(fill='both', expand=1)
        tree_vscroll_bar1.config(command=my_tree1.yview)
        tree_hscroll_bar1.config(command=my_tree1.xview)

        new_label1.config(text='Imported JSON Results - POST DATA CLEAN')
        tk.messagebox.showinfo('File Load Success', message='Success! - Data Cleaned for Imported JSON. '
                                                            'Click OK to save the file for future use')
        clean_json_data_save(out_df)

    else:
        # If user clicks on Cancel Button - Browse folder dialogue box
        pass


def clean_json_data_save(df):
    # To Get proper filename for later use to create json with same filename as csv
    head, tail = os.path.split(json_file_path)
    # Cleaned JSON file name will be prefixed with cleaned_.
    filename = 'cleaned_' + tail
    file = head + '/' + filename
    # Start Timer
    clean_json_time = time.time()

    result = df.to_json(orient='split')
    parsed = json.loads(result)

    # Check for old file with same name. If found, delete. Avoid any potential file corruption
    if os.path.exists(file):
        os.remove(file)
        print("Existing File Removed. Creation of New File")
        print(f"Writing to file => {file}")

    # Json File Creation
    with open(file, 'w') as jsoninspec:
        jsoninspec.write(json.dumps(parsed, sort_keys=True, indent=4))

    jsoninspec.close()
    print(f"--- New JSON File (Post Data Clean) Creation completed in {time.time() - clean_json_time:.3f} seconds ---")

    # Success Message. Stop Timer
    tk.messagebox.showinfo('File Load Success', message=f'Success! - File Save Success. Path \n {file}')

    # Method to check if Mean / Median / Mode button is required
    generate_mean_btn(df)


def generate_mean_btn(df):
    button_df = df
    # Obtain 'list' of Frame child elements
    frame_content = tab3_frame.winfo_children()
    # If the length of the list is greater than 5, Mean / Median / Mode button are present
    if len(frame_content) > 5:
        print('Button Exists!')
        # Bug: After the calculation buttons is shown, if the user imports a non ‘SCORE’ column json,
        # and then clicks any calculation button, it will show the previous result instead of an error message.
        # Fix: We take out the button and re-add them if necessary.
        for child in (tab3_frame.winfo_children())[5::]:
            child.destroy()
    # Logic to check if the data-frame has 'SCORE' column which is necessary for Mean / Median / Mode calculation
    if 'SCORE' in button_df.columns:

        # Create the Buttons
        # Object Creation
        mean_calc = DataCalculation()
        median_calc = DataCalculation()
        mode_calc = DataCalculation()

        # Create the Buttons.
        # Use of Lambda functions to ensure an action is executed only when clicked by the user.
        # This allows the user to pick and choose the data calculation option
        generate_calc_btn = ttk.Button(tab3_frame, text='Mean',
                                       command=lambda: mean_calc.data_calculations('Mean', button_df), width=15)
        generate_calc_btn.pack(padx=5, pady=10, side=tk.LEFT)
        generate_median_btn = ttk.Button(tab3_frame, text='Median',
                                         command=lambda: median_calc.data_calculations('Median', button_df), width=15)
        generate_median_btn.pack(padx=5, pady=10, side=tk.LEFT)
        generate_mode_btn = ttk.Button(tab3_frame, text='Mode',
                                       command=lambda: mode_calc.data_calculations('Mode', button_df), width=15)
        generate_mode_btn.pack(padx=5, pady=10, side=tk.LEFT)

    # JSON file without the Inspection Score - 'SCORE'. No Data Calculation Button Required
    else:
        print("Buttons Not Required")
        pass


def load_clean_json():
    json_path = askopenfilename(title='JSON File with Prefix - cleaned_*', filetypes=(('JSON Files', '*.json'),))
    json_import_time = time.time()
    if json_path:
        try:
            clean_json_path = r"{}".format(json_path)
            head, tail = os.path.split(clean_json_path)
            print(tail)
            if tail.startswith('cleaned'):
                # Data type set as object to prevent conversion of int to float
                clean_df = pd.read_json(clean_json_path, orient='split')

                clear_tree()
                print("Setting Up your Treeview")
                treeview_time = time.time()
                # Setup New Tree
                my_tree1["column"] = list(clean_df.columns)
                my_tree1["show"] = "headings"
                # Loop Through for handling the headers
                for column in my_tree1["column"]:
                    my_tree1.heading(column, text=column)

                # Put Data in Treeview
                df_rows = clean_df.to_numpy().tolist()
                for row in df_rows:
                    my_tree1.insert("", "end", values=row)

                print(f"--- Tree-view processing completed in {round(time.time() - treeview_time, 3)} seconds ---")
                my_frame.pack(before=import_csv_btn, fill='both', expand=1)
                my_tree.pack(fill='both', expand=1)
                tree_vscroll_bar.config(command=my_tree.yview)
                tree_hscroll_bar.config(command=my_tree.xview)

                new_label.config(text='Imported JSON Results. Choose Option from Below')

                my_frame1.pack(before=import_json_btn1, fill='both', expand=1)
                my_tree1.pack(fill='both', expand=1)
                tree_vscroll_bar1.config(command=my_tree1.yview)
                tree_hscroll_bar1.config(command=my_tree1.xview)

                new_label1.config(text='Imported JSON Results - POST DATA CLEAN')
                print(f"--- Clean JSON processing completed in {round(time.time() - json_import_time, 3)} seconds ---")
                generate_mean_btn(clean_df)
            else:
                tk.messagebox.showinfo('File Import - Unsuccessful',
                                       message=f'Use a Clean JSON autogenerated post "Import Raw JSON" Operation')
        except UnboundLocalError:
            print("UnboundLocalError: Please Enter a Valid CSV file & try")

        except ValueError:
            print("Unable to Open/Load Your File. Try Again!")
            tk.messagebox.showinfo('File Import - Unsuccessful',
                                   message=f'Use a Clean JSON autogenerated post "Import Raw JSON" Operation')


class DataCalculation:

    def data_calculations(self, calc_type, df):

        # Check for the SCORE column in the data-frame
        if 'SCORE' in df.columns:
            try:
                # To set 'SCORE' Column data-type as float to avoid error if loaded as object
                mean_df = pd.DataFrame(df.astype({'SCORE': float}))
                if calc_type == 'Mean':
                    print("=" * 15 + " MEAN SCORE - VENDOR" + "=" * 15)
                    # Calculate Mean
                    vendor_output = pd.DataFrame(mean_df.groupby('PE DESCRIPTION').SCORE.mean()).round(2)

                    print("=" * 15 + " MEAN SCORE - ZIP" + "=" * 15)
                    zip_output = pd.DataFrame(mean_df.groupby('FACILITY ZIP').SCORE.mean()).round(2)

                elif calc_type == 'Median':

                    print("=" * 15 + " MEDIAN SCORE - VENDOR" + "=" * 15)
                    # Calculate Median
                    vendor_output = pd.DataFrame(mean_df.groupby(['PE DESCRIPTION']).SCORE.median()).round(2)

                    print("=" * 15 + " MEDIAN SCORE - ZIP" + "=" * 15)
                    zip_output = pd.DataFrame(mean_df.groupby(['FACILITY ZIP']).SCORE.median()).round(2)

                else:
                    print("=" * 15 + " MODE SCORE -VENDOR" + "=" * 15)
                    # Calculate Mode
                    vendor_output = pd.DataFrame(mean_df.groupby('PE DESCRIPTION').SCORE.apply(lambda m: m.mode()))

                    print("=" * 15 + " MODE SCORE -ZIP" + "=" * 15)
                    zip_output = pd.DataFrame(mean_df.groupby('FACILITY ZIP').SCORE.apply(lambda m: m.mode()))

                vendor_output.reset_index(inplace=True)
                print(vendor_output)
                zip_output.reset_index(inplace=True)
                print(zip_output)

                new_window = tk.Toplevel()  # Create a new window to display the Data Calculation Score
                new_window.geometry('960x480')  # Set the dimension
                new_window.resizable(False, False)  # Disable resizing
                new_window.wm_title(f"=~= {calc_type} =~=")  # Title Name (Mean/Median/Mode)
                mean_frame = tk.Frame(new_window)
                mean_frame.pack()

                frame1 = ttk.LabelFrame(new_window, text="Vendor Type")
                frame1.place(height=440, width=460)  # Use of Geometry manager 'place'

                frame2 = ttk.LabelFrame(new_window, text="ZIP CODE")
                frame2.place(height=440, width=460, relx=0.51)  # Place the labelframe adjacent to each other

                # Tree-view Widget
                tv1 = ttk.Treeview(frame1)
                tv1.place(relheight=1, relwidth=1)

                # Setting up the scrollbar for both horizontal & vertical
                treescrolly = tk.Scrollbar(frame1, orient="vertical", command=tv1.yview)
                treescrollx = tk.Scrollbar(frame1, orient="horizontal", command=tv1.xview)
                tv1.configure(xscrollcommand=treescrollx.set, yscrollcommand=treescrolly.set)
                treescrollx.pack(side="bottom", fill="x")
                treescrolly.pack(side="right", fill="y")

                tv2 = ttk.Treeview(frame2)
                tv2.place(relheight=1, relwidth=1)

                tree2scrolly = tk.Scrollbar(frame2, orient="vertical", command=tv1.yview)
                tree2scrollx = tk.Scrollbar(frame2, orient="horizontal", command=tv1.xview)
                tv2.configure(xscrollcommand=tree2scrollx.set, yscrollcommand=tree2scrolly.set)
                tree2scrollx.pack(side="bottom", fill="x")
                tree2scrolly.pack(side="right", fill="y")

                tv1.delete(*tv1.get_children())
                tv1["column"] = list(vendor_output.columns)
                tv1["show"] = "headings"
                for column in tv1["columns"]:
                    tv1.heading(column, text=column)  # let the column heading = column name
                df_rows = vendor_output.to_numpy().tolist()  # turns the data-frame into a list of lists
                for row in df_rows:
                    tv1.insert("", "end", values=row)  # inserts each list into the tree-view.

                tv2.delete(*tv2.get_children())
                tv2["column"] = list(zip_output.columns)
                tv2["show"] = "headings"
                for column in tv2["columns"]:
                    tv2.heading(column, text=column)  # let the column heading = column name
                df_rows = zip_output.to_numpy().tolist()  # turns the data-frame into a list of lists
                for row in df_rows:
                    tv2.insert("", "end", values=row)  # inserts each list into the tree-view.

                close_btn = ttk.Button(new_window, text="Close", command=new_window.destroy)
                close_btn.pack(side=tk.BOTTOM, padx=10, pady=10)

            except UnboundLocalError:
                print("UnboundLocalError: Please Enter a Valid JSON file & try")

            except KeyError:
                print("It Seems the File you have uploaded cannot calculate Mean / Median / Mode")
                tk.messagebox.showinfo('File Import - Unsuccessful',
                                       message='The File you have uploaded cannot calculate Mean / Median / Mode')

            except AttributeError:
                print("Attribute Error - It Seems the File you have uploaded cannot calculate Mean / Median / Mode")
                tk.messagebox.showinfo('File Import - Unsuccessful',
                                       message='The File you have uploaded cannot calculate Mean / Median / Mode')
            except:
                tk.messagebox.showinfo('File Import - Unsuccessful',
                                       message='Some Problem. Close Program and Try Again')
        else:
            tk.messagebox.showinfo('File Import - Unsuccessful',
                                   message='The File you have uploaded cannot calculate Mean / Median / Mode')


"""
Phase III - Data Load & Visualise
"""

"""

"""


def json_file_load():
    # To ensure only JSON files are selected
    # User is expected to load multiple files
    clean_json_paths = tk.filedialog.askopenfilenames(parent=root,
                                                      title='Open Cleaned JSON Files',
                                                      filetypes=(('JSON Files', '*.json'),))
    try:
        if clean_json_paths:
            clean_json_paths = root.tk.splitlist(clean_json_paths)
            return clean_json_paths

    except UnboundLocalError:
        print("UnboundLocalError: Please load valid JSON files (prefixed cleaned_*) file & try")
    except ValueError:
        print("Unable to Open/Load Your File. Try Again!")


def json_dframe_prep():
    try:
        json_file_list = json_file_load()
        json_file_dict = {}
        """
        To ensure file names are not hard coded, we will be looking based on the column names
        as client brief states -
        It should be assumed that this program will be able to handle other sets of data generated from the same source, 
        i.e. data with the same column row headings but containing different values and anomalies.
        """
        for i in range(len(json_file_list)):
            json_file_dict[i] = pd.read_json(json_file_list[i], orient='split')
            if 'SCORE' in json_file_dict[i]:
                if 'VENUE CAPACITY' in json_file_dict[i]:
                    inspec_df = pd.DataFrame(json_file_dict[i])
                else:
                    tk.messagebox.showinfo('File Import - Unsuccessful',
                                           message='Some Problem. You may have uploaded the raw JSON.'
                                                   'Please try with cleaned JSON files')
                    break
            elif 'OWNER ADDRESS' in json_file_dict[i]:
                if 'VENUE CAPACITY' in json_file_dict[i]:
                    invnt_df = pd.DataFrame(json_file_dict[i])
                else:
                    tk.messagebox.showinfo('File Import - Unsuccessful',
                                           message='Some Problem. You may have uploaded the raw JSON.'
                                                   'Please try with cleaned JSON files')
                    break
            elif 'VIOLATION  STATUS' in json_file_dict[i]:
                violation_df = pd.DataFrame(json_file_dict[i])
                tk.messagebox.showinfo('File Import - Successful', message='Cleaned JSON Files successfully loaded. '
                                                                           'Continue with Data Visualisation.\n Do select a radio button before button click')

                new_label2.config(text='File Loaded Successfully!| Please use radio button to select an option')

            else:
                tk.messagebox.showinfo('File Import - Unsuccessful',
                                       message='Some Problem. Please use JSON files which were cleaned')
                break
    except UnboundLocalError:
        print("UnboundLocalError: Please load valid JSON files (prefixed cleaned_*) file & try")

    except TypeError:
        print("UnboundLocalError: Please load valid JSON files (prefixed cleaned_*) file & try")

    try:
        # Trimming down the dataframe keeping only the required column
        sub_inspec_df = inspec_df[['OWNER NAME', 'FACILITY ZIP', 'FACILITY CITY', 'SERIAL NUMBER']]
        sub_viol_df = violation_df[['SERIAL NUMBER', 'VIOLATION CODE']]

        # Data Merging of data frames
        violation_merge_df = sub_inspec_df.merge(sub_viol_df, on='SERIAL NUMBER', how='inner')
        graph1 = pd.DataFrame(violation_merge_df.groupby(['VIOLATION CODE']).size().to_frame('VIOLATION SIZE'))
        # To remove multi-index
        graph1.reset_index(inplace=True)
        # Sorting by column
        graph1.sort_values(by=['VIOLATION SIZE'], inplace=True)

        # Object Creation for class DataVisuals
        data_visual = DataVisuals()

        # We are only extracting the main zip code and excluding the '+4 Codes'
        # https://en.wikipedia.org/wiki/ZIP_Code
        violation_merge_df['FACILITY ZIP'] = violation_merge_df['FACILITY ZIP'].str[0:5]
        # Useful for obtaining a numeric representation to create 'Categories'
        # required for graphical representation
        violation_merge_df['CAT_VIOLATION'] = pd.factorize(violation_merge_df['VIOLATION CODE'])[0]
        violation_merge_df['CAT_FACILITY_CITY'] = pd.factorize(violation_merge_df['FACILITY CITY'])[0]
        violation_merge_df['CAT_FACILITY_ZIP'] = pd.factorize(violation_merge_df['FACILITY ZIP'])[0]
        violation_merge_df['CAT_OWNER'] = pd.factorize(violation_merge_df['OWNER NAME'])[0]

        # Radio Button Selection - Works like Switch Condition
        def selection():
            global min_val, max_val
            selected_val = var.get()
            if selected_val == 1:
                min_val = '0'
                max_val = '500'
            elif selected_val == 2:
                min_val = '500'
                max_val = '5000'
            elif selected_val == 3:
                min_val = '5000'
                max_val = '25000'
            else:
                min_val = '25000'
                max_val = '99999999'

        # Holds an integer
        var = tk.IntVar()

        # Frame for 'Establishments Committed per each type of Violation' radiobutton options
        frame1 = ttk.LabelFrame(tab4_frame, text="Establishments Committed\n per each type of Violation")
        frame1.pack(padx=5, pady=10, side=tk.LEFT)

        # Radio Button Widgets
        r1 = ttk.Radiobutton(frame1, text='0-500', variable=var, command=selection, value=1)
        r1.pack(padx=5, pady=10, side=tk.TOP)

        r2 = ttk.Radiobutton(frame1, text='500-5000', variable=var, command=selection, value=2)
        r2.pack(padx=5, pady=10, side=tk.TOP)

        r3 = ttk.Radiobutton(frame1, text='5000-25000', variable=var, command=selection, value=3)
        r3.pack(padx=5, pady=10, side=tk.TOP)

        r4 = ttk.Radiobutton(frame1, text='25000-Max', variable=var, command=selection, value=4)
        r4.pack(padx=5, pady=10, side=tk.TOP)

        generate_graph_btn = ttk.Button(frame1, text='Violations Graphs',
                                        command=lambda: data_visual.data_violations_visuals(graph1, min_val, max_val),
                                        width=20)
        generate_graph_btn.pack(padx=5, pady=10, side=tk.BOTTOM)

        # Radio Button Selection - Works like Switch Condition
        # Sample count is added here to produce faster output response
        def sample_selection():
            global sample_count
            selected_val = var1.get()
            if selected_val == 1:
                sample_count = '20000'
            elif selected_val == 2:
                sample_count = '50000'
            elif selected_val == 3:
                sample_count = '100000'
            else:
                sample_count = '200000'

        var1 = tk.IntVar()

        # Frame for choosing Sample Size - Location Specific Violation
        frame2 = ttk.LabelFrame(tab4_frame, text="Choose Sample Size \n- Location Specific Violation")
        frame2.pack(padx=5, pady=10, side=tk.LEFT)

        # Radio Button Widgets
        r5 = ttk.Radiobutton(frame2, text='20,000 (Fast Response)', variable=var1, command=sample_selection, value=1)
        r5.pack(padx=5, pady=10, side=tk.TOP)

        r6 = ttk.Radiobutton(frame2, text='50,000', variable=var1, command=sample_selection, value=2)
        r6.pack(padx=5, pady=10, side=tk.TOP)

        r7 = ttk.Radiobutton(frame2, text='100,000', variable=var1, command=sample_selection, value=3)
        r7.pack(padx=5, pady=10, side=tk.TOP)

        r8 = ttk.Radiobutton(frame2, text='200,000 (Slow Response)', variable=var1, command=sample_selection, value=4)
        r8.pack(padx=5, pady=10, side=tk.TOP)

        # Button to display graph for client requirement:
        # Number of violations commited per vendor
        generate_graph_btn1 = ttk.Button(frame2, text='Violations - Location Specific',
                                         command=lambda: data_visual.data_analysis_visuals(violation_merge_df,
                                                                                           'VIOLATION-1'), width=20)
        generate_graph_btn1.pack(padx=5, pady=10, side=tk.BOTTOM)

    # Error Message
    except UnboundLocalError:
        tk.messagebox.showinfo('Unable to Calculate Violations',
                               message='We are unable to Calculate Violations - Data Analysis, '
                                       'please use the correct files')


class DataVisuals:

    def data_violations_visuals(self, graphdf, minval, maxval):

        new_graph_window = tk.Toplevel()
        new_graph_window.geometry('1000x700')
        new_graph_window.resizable(False, False)
        new_graph_window.wm_title("Violations Graphs")
        graph_frame = tk.Frame(new_graph_window)
        button_frame = tk.Frame(graph_frame)
        graph_frame.pack(side=tk.TOP)
        button_frame.pack(side=tk.BOTTOM)

        graph_specs = graphdf[(graphdf['VIOLATION SIZE'] >= int(minval)) & (graphdf['VIOLATION SIZE'] <= int(maxval))]
        facility_list = graph_specs['VIOLATION CODE'].values.tolist()
        size_list = graph_specs['VIOLATION SIZE'].values.tolist()

        # width and height in inches.
        fig = plt.figure(figsize=(15, 8))
        axes = fig.add_axes([0.1, 0.1, 0.8, 0.8])
        # Creation of Matplot Lib - Horizontal Bar Graph
        axes.barh(facility_list, size_list)

        # Setting Title based on the radio button input from user
        if maxval == '99999999':
            axes.set_title(f'Violation Score - Number of Establishments ({minval}-Max) Per Each Violations Code')
        else:
            axes.set_title(f'Violation Score - Number of Establishments ({minval}-{maxval}) Per Each Violations Code')
        # Setting X-Y Axis Labels
        axes.set_ylabel('Type of Violations')
        axes.set_xlabel('No. Establishments')

        # MatplotLib's FigureCanvasTkAgg method to embed graphs to UI
        canvas = FigureCanvasTkAgg(fig, master=graph_frame)  # Figure Canvas used for plotting
        canvas.draw()

        # MatplotLib's NavigationToolbar2Tk method to provide toolbar option to user like - Save file
        toolbar = NavigationToolbar2Tk(canvas, graph_frame)  # Navigation Toolbar
        toolbar.update()

        quit_btn = ttk.Button(master=button_frame, text="Quit", command=new_graph_window.destroy, width=10)
        quit_btn.pack(side=tk.LEFT, padx=10, pady=10)

        # Geometry Manager to pack the widgets
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    def data_analysis_visuals(self, graphdf, inputval):

        data_analysis_time = time.time()
        new_graph_window = tk.Toplevel()
        new_graph_window.geometry('1000x700')
        new_graph_window.resizable(False, False)
        new_graph_window.wm_title("Violations - Data Analysis")
        graph_frame = tk.Frame(new_graph_window)
        button_frame = tk.Frame(graph_frame)
        graph_frame.pack(side=tk.TOP)
        button_frame.pack(side=tk.BOTTOM)

        fig = plt.figure(figsize=(10, 8))
        axes = fig.add_axes([0.1, 0.1, 0.8, 0.8])
        graphdf = graphdf.sample(int(sample_count))

        if inputval == 'VIOLATION-1':
            # Use of Kernel Density Estimate to generate graph for requirement
            # No. of violations committed per vendor
            sns.kdeplot(graphdf.CAT_VIOLATION, graphdf.CAT_FACILITY_CITY, cmap="YlGnBu", shade=True, cbar=True)
            axes.set_title('Data Analysis - Location Specific Facilities & Violations')
            print(f"--- Data Graph  processing for 'Location Specific Facilities & Violations'completed in "
                  f"{time.time() - data_analysis_time:.3f} seconds ---")
        else:
            sns.kdeplot(graphdf.CAT_OWNER, graphdf.CAT_FACILITY_ZIP, cmap="PuBuGn", shade=True, cbar=True)
            axes.set_title('Data Analysis - Violations Committed by Vendor & Zip Code')
            print(f"--- Data Graph  processing for 'Violations Committed by Vendor & Zip Code'completed in "
                  f"{time.time() - data_analysis_time:.3f} seconds ---")

        # Figure Canvas used for plotting.
        canvas = FigureCanvasTkAgg(fig, master=graph_frame)
        canvas.draw()

        # Navigation Toolbar
        toolbar = NavigationToolbar2Tk(canvas, graph_frame)
        toolbar.update()

        # Button to Produce Grapg - Tendency in specific location to have more violations
        loc_violation_btn = ttk.Button(master=button_frame, text="Owner-Violation/ZipCode",
                                       command=lambda: self.data_analysis_visuals(graphdf, 'VIOLATION-2'),
                                       width=30)
        loc_violation_btn.pack(side=tk.LEFT, padx=10, pady=10)

        quit_btn = ttk.Button(master=button_frame, text="Quit", command=new_graph_window.destroy, width=10)
        quit_btn.pack(side=tk.LEFT, padx=10, pady=10)

        # Geometry Manager to pack the widgets
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
""" 
Common Functions
"""


# To Clear if any previous tree view was displayed to the user
def clear_tree():
    my_tree.delete(*my_tree.get_children())
    my_tree1.delete(*my_tree1.get_children())


# To Quit the application
def exit_application():
    close_app = tk.messagebox.askquestion('Exit', 'Are you sure you want to exit the application',
                                          icon='warning')
    if close_app == 'yes':
        root.quit()
        root.destroy()

"""
Main TK Inter Layout Code
"""
root = tk.Tk()                  # Creation of Root Window
root.geometry('1080x480')       # Set the Frame size
root.resizable(False, False)    # Set to False to prevent resizing of the window
root.title("Data Import/ Format / Convert / Visualise Utility")  # Title of Root Window

# Use of ttk - Notebook
tabOptions = ttk.Notebook(root)
tabOptions.pack(fill='both', expand=True)

# Multiple Tabs within the Notebook (Multiple Colour Codes)
tab1_frame = tk.Frame(tabOptions, bg='#E0FFFF')
tab2_frame = tk.Frame(tabOptions, bg='#fed8b1')
tab3_frame = tk.Frame(tabOptions, bg='#FFFF99')
tab4_frame = tk.Frame(tabOptions, bg='#98FB98')

# Add Tabs with Text for each tabs
tabOptions.add(tab1_frame, text='Welcome!')
tabOptions.add(tab2_frame, text='Data Import & Translate')
tabOptions.add(tab3_frame, text='Data Clean & Calculate')
tabOptions.add(tab4_frame, text='Data Load & Visualisation')

# Welcome Tab
# Grid places the label at specific co-oridnates of the frame
# columnspan to span widgets to multiple column
ttk.Label(tab1_frame, text="Welcome to myPyDataUtil - Data Import / Convert / Clean / Visualise Utility",
          font='arial 16 bold').grid(column=1, row=0, columnspan=3, padx=10, pady=10, sticky='W')

ttk.Label(tab1_frame, text="Use the tabs above to carry out various operations. "
                           "Info about operations processed by myPyDataUtil is mentioned below",
          font='arial 14 italic').grid(column=1, row=1, columnspan=3, padx=5, pady=5, sticky='W')

ttk.Label(tab1_frame, text="Data Import & Translate",
          font='arial 13 bold').grid(column=1, row=2, padx=5, pady=5, sticky='W')
ttk.Label(tab1_frame, text="Use this Option to perform: "
                           "\n=> Load your CSV & Translate to JSON"
                           "\n=> JSON File Save"
                           "\n=> Display your loaded CSV file (Filtered View)"  
                           "\n=> Exit", font='arial 12').grid(column=1, row=3, padx=5, pady=5, sticky='W')

ttk.Label(tab1_frame, text="Data Clean & Calculate",
          font='arial 13 bold').grid(column=2, row=2, padx=5, pady=5, sticky='W')

ttk.Label(tab1_frame, text="Use this Option to perform: "
                           "\n=> Data Clean"
                           "\n=> Prepared Dataset (JSON) - Save"
                           "\n=> Load Prepared Dataset - JSON"
                           "\n=> Calculate Mean / Median / Mode Scores"
                           "\n=> Exit", font='arial 12').grid(column=2, row=3, padx=5, pady=5, sticky='W')

ttk.Label(tab1_frame, text="Data Load & Visualisation",
          font='arial 13 bold').grid(column=3, row=2, padx=5, pady=5, sticky='W')

ttk.Label(tab1_frame, text="Use this Option to perform: "
                           "\n=> Load Prepared DataSet"
                           "\n=> Number of Establishments/Each Violations Code - Display Graph"
                           "\n=> Violations - Location Specific - Display Graphs"
                           "\n=> Exit", font='arial 12').grid(column=3, row=3, padx=5, pady=5, sticky='W')
# Exit Button
exit1_btn = ttk.Button(tab1_frame, text='Exit', command=exit_application, width=10).grid(column=2, row=6, padx=5, pady=5)


"""
Data Import & Visualise
"""

new_label = ttk.Label(tab2_frame, text="Please Select a Raw CSV File to Import")
new_label.pack()
my_frame = tk.Frame(tab2_frame)

# Add Scrollbar widgets for the imported csv view
tree_vscroll_bar = ttk.Scrollbar(my_frame, orient=tk.VERTICAL)
tree_hscroll_bar = ttk.Scrollbar(my_frame, orient=tk.HORIZONTAL)
tree_vscroll_bar.pack(side=tk.RIGHT, fill=tk.Y)
tree_hscroll_bar.pack(side=tk.BOTTOM, fill=tk.X)
my_tree = ttk.Treeview(my_frame, yscrollcommand=tree_vscroll_bar.set, xscrollcommand=tree_hscroll_bar.set)

import_csv_btn = ttk.Button(tab2_frame, text='Import CSV', command=csv_frame_format, width=10)
import_csv_btn.pack(padx=5, pady=10, side=tk.LEFT)

exit_btn = ttk.Button(tab2_frame, text='Exit', command=exit_application, width=10)
exit_btn.pack(padx=5, pady=10, side=tk.LEFT)

"""
Data Clean & Calculate
"""
new_label1 = ttk.Label(tab3_frame, text="Import Raw JSON - Import JSON for Data Clean | "
                                       "Load Clean JSON - Import Cleaned JSON (Prefix - cleaned_)")
new_label1.pack()
my_frame1 = tk.Frame(tab3_frame)

# Add Scrollbar widgets for the cleaned json view
tree_vscroll_bar1 = ttk.Scrollbar(my_frame1, orient=tk.VERTICAL)
tree_hscroll_bar1 = ttk.Scrollbar(my_frame1, orient=tk.HORIZONTAL)
tree_vscroll_bar1.pack(side=tk.RIGHT, fill=tk.Y)
tree_hscroll_bar1.pack(side=tk.BOTTOM, fill=tk.X)
my_tree1 = ttk.Treeview(my_frame1, yscrollcommand=tree_vscroll_bar1.set, xscrollcommand=tree_hscroll_bar1.set)

import_json_btn1 = ttk.Button(tab3_frame, text='Import Raw JSON', command=json_data_clean, width=15)
import_json_btn1.pack(padx=5, pady=10, side=tk.LEFT)

import_json_btn2 = ttk.Button(tab3_frame, text='Load Clean JSON', command=load_clean_json, width=15)
import_json_btn2.pack(padx=5, pady=10, side=tk.LEFT)

exit_btn = ttk.Button(tab3_frame, text='Exit', command=exit_application, width=10)
exit_btn.pack(padx=5, pady=10, side=tk.LEFT)

"""
Data Load & Visualise
"""
my_frame2 = tk.Frame(tab4_frame)

new_label2 = ttk.Label(tab4_frame, text="Load Clean JSON Files (File Prefix - cleaned_*)")
new_label2.pack()

import_json_btn3 = ttk.Button(tab4_frame, text='Load Clean JSON Files', command=json_dframe_prep, width=20)
import_json_btn3.pack(padx=5, pady=10, side=tk.LEFT)

exit_btn = ttk.Button(tab4_frame, text='Exit', command=exit_application, width=10)
exit_btn.pack(padx=5, pady=10, side=tk.LEFT)

# Method to execute the tkinter window until user closes the session
# or click exit button
root.mainloop()