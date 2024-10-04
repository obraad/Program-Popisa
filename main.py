import sys, os
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QHBoxLayout, \
    QGridLayout, QMessageBox, QCalendarWidget, QDialog, QVBoxLayout, QFormLayout, QSpacerItem, QSizePolicy, QTextEdit, \
    QListWidgetItem, QListWidget

from sqlalchemy import create_engine, Column, Integer, Sequence, DateTime, String, desc, inspect, text
from sqlalchemy.orm import declarative_base, sessionmaker, make_transient
from datetime import datetime, timedelta
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QSize, QPropertyAnimation, QTimer, QEvent
from deepdiff import DeepDiff

# SQLAlchemy setup
Base = declarative_base()


class CustomLineEdit(QLineEdit):
    def __init__(self, parent=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parent = parent  # Store a reference to the parent class (e.g., BettingShiftTracker)

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            try:
                self.call_a()  # Trigger the comparison when Enter is pressed
                # Find the index of the current widget in current_labels
                current_index = self.parent.current_labels.index(self)
                # Move focus to the next widget in current_labels if there is one
                if current_index < len(self.parent.current_labels) - 1:
                    next_widget = self.parent.current_labels[current_index + 1]
                    next_widget.setFocus()
                    next_widget.selectAll()  # Select all text in the next widget
                # Jumping to BINGO Label after slot machine fields are done
                elif current_index == 3:
                    self.parent.group_edits[0].setFocus()
                    self.parent.group_edits[0].selectAll()  # Select all text in the BINGO label
            except:
                self.focusNextChild()  # Fallback to default focus handling
        else:
            super().keyPressEvent(event)  # Handle other key events normally
            self.call_a()  # Trigger comparison on any key press

    def call_a(self):
        if hasattr(self.parent, 'compare_with_saved_state'):
            try:
                self.parent.compare_with_saved_state()  # Call the function from the parent class
            except Exception:
                pass


class CustomLineEditZ(QLineEdit):
    def __init__(self, parent=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parent = parent

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            # Check if this is the group_edits[2] widget
            if self == self.parent.group_edits[2]:
                # Simulate the button click when pressing Enter on group_edits[2]
                self.parent.calculate_btn.click()
                self.focusNextChild()
            else:
                # Move focus to the next widget otherwise
                self.focusNextChild()
            self.call_a()  # Trigger comparison after handling the focus
        else:
            super().keyPressEvent(event)  # Handle other key events normally
            self.call_a()  # Trigger comparison on any key press

    def call_a(self):
        if hasattr(self.parent, 'compare_with_saved_state'):
            try:
                self.parent.compare_with_saved_state()  # Call the function from the parent class
            except Exception:
                pass


class slotMachineState(Base):
    __tablename__ = 'slot_machine_state'
    id = Column(Integer, Sequence('slot_machine_id_seq'), primary_key=True)
    slot_machine_1 = Column(Integer, default=0)
    slot_machine_2 = Column(Integer, default=0)
    slot_machine_3 = Column(Integer, default=0)
    slot_machine_4 = Column(Integer, default=0)
    cash_balance = Column(Integer, default=0)

    group_ticket = Column(Integer, default=0)
    group_bingo = Column(Integer, default=0)
    group_live = Column(Integer, default=0)

    total_profit_loss = Column(Integer, default=0)
    total_slot_machines_difference = Column(Integer, default=0)

    previous_slot_machine_1 = Column(Integer, default=0)
    previous_slot_machine_2 = Column(Integer, default=0)
    previous_slot_machine_3 = Column(Integer, default=0)
    previous_slot_machine_4 = Column(Integer, default=0)

    previous_cash_balance = Column(Integer, default=0)
    datum = Column(DateTime, default=datetime.now)
    smena = Column(String)

    previous_difference_1 = Column(Integer, default=0)
    previous_difference_2 = Column(Integer, default=0)
    previous_difference_3 = Column(Integer, default=0)
    previous_difference_4 = Column(Integer, default=0)

    monthly_slot_machine_1 = Column(Integer, default=0)
    monthly_slot_machine_2 = Column(Integer, default=0)
    monthly_slot_machine_3 = Column(Integer, default=0)
    monthly_slot_machine_4 = Column(Integer, default=0)

    message_list = Column(String, default="")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class DeletedCensus(Base):
    __tablename__ = 'deleted_census'
    id = Column(Integer, Sequence('deleted_census_id_seq'), primary_key=True, autoincrement=True)
    datum = Column(DateTime, default=datetime.now)
    smena = Column(String)
    vreme_brisanja = Column(DateTime, default=datetime.now)

    # Dodaj podatke o aparatima
    slot_machine_1 = Column(Integer, default=0)
    slot_machine_2 = Column(Integer, default=0)
    slot_machine_3 = Column(Integer, default=0)
    slot_machine_4 = Column(Integer, default=0)
    cash_balance = Column(Integer, default=0)

    group_ticket = Column(Integer, default=0)
    group_bingo = Column(Integer, default=0)
    group_live = Column(Integer, default=0)

    total_profit_loss = Column(Integer, default=0)
    total_slot_machines_difference = Column(Integer, default=0)

    previous_slot_machine_1 = Column(Integer, default=0)
    previous_slot_machine_2 = Column(Integer, default=0)
    previous_slot_machine_3 = Column(Integer, default=0)
    previous_slot_machine_4 = Column(Integer, default=0)

    previous_cash_balance = Column(Integer, default=0)

    previous_difference_1 = Column(Integer, default=0)
    previous_difference_2 = Column(Integer, default=0)
    previous_difference_3 = Column(Integer, default=0)
    previous_difference_4 = Column(Integer, default=0)

    monthly_slot_machine_1 = Column(Integer, default=0)
    monthly_slot_machine_2 = Column(Integer, default=0)
    monthly_slot_machine_3 = Column(Integer, default=0)
    monthly_slot_machine_4 = Column(Integer, default=0)

    message_list = Column(String, default="")


home_directory = os.path.expanduser('~')

# Define the path relative to the user's home directory
db_directory = os.path.join(home_directory, 'Documents', 'Popis Kladionice')
os.makedirs(db_directory, exist_ok=True)

# Create the engine with a database file in the user's documents directory
engine = create_engine(f'sqlite:///{db_directory}/betting_shift_tracker.db')

# Define the Base and create the tables
Base.metadata.create_all(engine)

# Create a session
Session = sessionmaker(bind=engine)
session = Session()


# Define the path relative to the user's home directory
deleted_db_directory = os.path.join(home_directory, 'Documents', 'Popis Kladionice')
os.makedirs(deleted_db_directory, exist_ok=True)

# Kreiraj novi engine za bazu obrisanih popisa
deleted_engine = create_engine(f'sqlite:///{deleted_db_directory}/deleted_censuses.db')

# Kreiraj tabele za bazu obrisanih popisa
Base.metadata.create_all(deleted_engine)

# Kreiraj sesiju za novu bazu
DeletedSession = sessionmaker(bind=deleted_engine)
deleted_session = DeletedSession()


def resource_path(relative_path):
    """ Get absolute path to resource, works for both dev and PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


class BettingShiftTracker(QWidget):
    def __init__(self):
        super().__init__()
        self.current_record_index = 0
        self.current_record = 0
        self.is_reviewing_history = False
        self.changed = False
        self.red_set = False
        self.records = []  # List that will hold records for history
        self.initUI()
        self.load_previous_state()
        self.pass_notebook_states()
        self.saved_state = None

    def open_money_counting_dialog(self):
        dialog = MoneyCountingDialog(self, self.current_cash_balance_edit)
        dialog.exec_()

    def create_hover_animation(self, label, start_width, end_width):
        # Animation for width change
        animation = QPropertyAnimation(label, b"minimumWidth")
        animation.setDuration(300)  # Duration of animation in milliseconds
        animation.setStartValue(start_width)
        animation.setEndValue(end_width)
        return animation

    # Function for showing hover effect
    def on_enter(self, label, animation):
        animation.setDirection(QPropertyAnimation.Forward)
        animation.start()

    # Function for deleting hover effect
    def on_leave(self, label, animation):
        animation.setDirection(QPropertyAnimation.Backward)
        animation.start()

    def change_date_to_yesterday(self):
        self.yesterday = datetime.now() - timedelta(days=1)
        self.shift = "Druga smena"
        if str(f'{self.yesterday.strftime("%d-%m-%Y")} - {self.shift}') == str(self.date_label.text()):
            QMessageBox.warning(self, 'Greška', 'Već ste vratili datum.')
        else:
            self.compare_with_saved_state()

            QMessageBox.information(self, 'Uspeh', 'Uspešno ste vratili datum.')
        self.date_label.setText(f'{self.yesterday.strftime("%d-%m-%Y")} - {self.shift}')
        self.changed = True

    def change_shift_to_second(self):
        day = self.records[self.current_record_index]
        day.smena = "Druga smena"
        session.commit()
        self.date_label.setText(f'{day.datum.strftime("%d-%m-%Y")} - {day.smena}')
        self.change_shift_button.setVisible(False)
        QMessageBox.information(self, 'Uspeh', 'Smena je uspešno promenjena u Drugu smenu.')

    def initUI(self):
        self.setWindowIcon(QIcon(resource_path('logo.png')))
        self.setStyleSheet("""
            QWidget {
                background-color: white;
            }
            QLabel {
                font-size: 14px;
                color: #333;
            }
            QLineEdit {
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                padding: 5px;
                border-radius: 5px;
            }
            QLineEdit:hover {
                border: 2px solid #4CAF50;
            }
            QLineEdit:focus {
                border: 2px solid #4CAF50;  /* Highlight with green border */
                background-color: #e0ffe0;  /* Slightly different background when focused */
            }
            QPushButton {
                font-weight: bold;
                background-color: #4CAF50;
                color: white;
                border-radius: 10px;
                padding: 5px;
                border: none;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.setFixedSize(665, 538)
        main_layout = QVBoxLayout()

        # Determine shift based on current time
        self.current_time = datetime.now().time()
        self.shift = "Prva smena" if self.current_time < datetime.strptime("18:00", "%H:%M").time() else "Druga smena"

        # Top horizontal layout for the Date and "Count Money" button
        top_layout = QHBoxLayout()
        self.date_label = QLabel(f'{datetime.now().strftime("%d-%m-%Y")} - {self.shift}')
        self.date_label.setStyleSheet("""
            QLabel {
                font-size:14px;
                background-color: white;
                border: 1px solid #ccc;
                color: green;
                font-family: Montserrat Black;
                padding: 10px;
                border-radius: 12px;
            }
            QLabel:hover {
                background-color: #fff1b8;  /* Lighter green on hover */
            }
        """)
        top_layout.addWidget(self.date_label)
        
        # Creating a button to change date to yesterday's
        self.change_date_button = QPushButton("", self)
        self.change_date_button.setIcon(QIcon(resource_path('previous_date.png')))
        self.change_date_button.setStyleSheet("background-color:transparent")
        self.change_date_button.setFixedSize(40, 40)  # Slightly bigger button for modern feel
        self.change_date_button.setIconSize(QSize(30, 30))
        top_layout.addWidget(self.change_date_button)
        self.change_date_button.setStyleSheet("""
                    QPushButton {
                        background-color: transparent;
                        border: none;

                    }
                    QPushButton:hover {
                        background-color: transparent;  /* Ensure background remains transparent */
                    }
                """)
        self.change_date_button.installEventFilter(self)  # Install event filter for hover events
        self.change_date_button.clicked.connect(self.change_date_to_yesterday)
        
        # Creating a button to change shift from first to second
        self.change_shift_button = QPushButton("", self)
        self.change_shift_button.setVisible(False)
        self.change_shift_button.setIcon(QIcon(resource_path('arrow_up.png')))
        self.change_shift_button.setStyleSheet("background-color:transparent")
        self.change_shift_button.setFixedSize(40, 40)  # Slightly bigger button for modern feel
        self.change_shift_button.setIconSize(QSize(30, 30))
        top_layout.addWidget(self.change_shift_button)
        self.change_shift_button.setStyleSheet("""
                            QPushButton {
                                background-color: transparent;
                                border: none;

                            }
                            QPushButton:hover {
                                background-color: transparent;  /* Ensure background remains transparent */
                            }
                        """)
        self.change_shift_button.installEventFilter(self)  # Install event filter for hover events
        self.change_shift_button.clicked.connect(self.change_shift_to_second)

        # Spacer to push the button to the right
        top_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        # Creating a button for money counting
        count_money_button = QPushButton("", self)
        count_money_button.setIcon(QIcon(resource_path('math.png')))
        count_money_button.setStyleSheet("background-color:transparent")
        count_money_button.setFixedSize(40, 40)  # Slightly bigger button for modern feel
        count_money_button.setIconSize(QSize(30, 30))
        count_money_button.clicked.connect(self.open_money_counting_dialog)
        top_layout.addWidget(count_money_button)
        count_money_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;

            }
            QPushButton:hover {
                background-color: transparent;  /* Ensure background remains transparent */
            }
        """)
        count_money_button.setIconSize(QSize(30, 30))  # Normal icon size
        count_money_button.installEventFilter(self)  # Install event filter for hover events

        # Add the top layout components to the main layout
        main_layout.addLayout(top_layout)

        # Grid layout for the rest of the UI elements (slot_machine states)
        self.grid_layout = QGridLayout()

        current_state_title = QLabel("TRENUTNA STANJA APARATA")
        current_state_title.setAlignment(Qt.AlignHCenter)
        current_state_title.setStyleSheet("""
            QLabel {
                font-size:14px;
                background-color: #e0ffe0;
                border: 1px solid #ccc;
                color: #4CAF50;
                font-family: Montserrat Black;
                font-style: italic;
                padding: 3px;
                padding-bottom: 5px;
                border-radius: 10px;
            }
            QLabel:hover {
                background-color: #c9ffc9;  /* Lighter green on hover */
            }
        """)
        self.grid_layout.addWidget(current_state_title, 0, 0, 1, 2)  # Span across two columns

        previous_state_title = QLabel("POČETNA STANJA APARATA")
        previous_state_title.setStyleSheet("""
            QLabel {
                font-size:14px;
                background-color: #e0ffe0;
                border: 1px solid #ccc;
                color: #4CAF50;
                font-family: Montserrat Black;
                font-style: italic;
                padding: 3px;
                padding-bottom: 5px;
                border-radius: 10px;
            }
            QLabel:hover {
                background-color: #c9ffc9;  /* Lighter green on hover */
            }
        """)
        previous_state_title.setAlignment(Qt.AlignHCenter)
        self.grid_layout.addWidget(previous_state_title, 0, 2, 1, 4)  # Span across two columns

        # Creating the lists that we will use later on
        self.current_labels = []
        self.previous_labels = []
        self.difference_labels = []

        self.previous_layouts = []  # Store references to each previous_layout

        for i in range(4):
            # Create a horizontal layout for each row
            current_layout = QHBoxLayout()
            previous_layout = QHBoxLayout()  # Create a new QHBoxLayout for each row

            # Showing number next to the field where current values are displayed
            number_label_current = QLabel(f'{i + 1}')
            number_label_current.setStyleSheet("""
                QLabel {
                    background-color: #4CAF50;
                    color: white;
                    font-size: 14px;
                    font-family: Montserrat Black;
                    font-style: italic;
                    padding: 5px;
                    border-radius: 5px;
                }
                QLabel:hover {
                    background-color: #45a049;  /* Lighter green on hover */
                }
            """)
            number_label_current.setFixedWidth(38)
            number_label_current.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            
            # Showing number next to the field where previous values are displayed
            number_label_previous = QLabel(f'{i + 1}')
            number_label_previous.setFixedWidth(38)
            number_label_previous.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            number_label_previous.setStyleSheet("""
                QLabel {
                    background-color: #4CAF50;
                    color: white;
                    font-size: 14px;
                    font-family: Montserrat Black;
                    font-style: italic;
                    padding: 5px;
                    border-radius: 5px;
                }
                QLabel:hover {
                    background-color: #45a049;  /* Lighter green on hover */
                }
            """)
            
            current_edit = CustomLineEdit(self)
            current_edit.setStyleSheet("font-family: Montserrat;Font-weight:bold;font-size:14px;")

            # Add number and input field to current layout
            current_layout.addWidget(number_label_current)
            current_layout.addWidget(current_edit)

            # Previous state labels
            previous_edit = CustomLineEdit(self)
            previous_edit.setStyleSheet("font-family: Montserrat;Font-weight:bold;font-size:14px;")
            previous_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            previous_edit.setReadOnly(True)

            # Set alignment and expand policy for previous_layout
            previous_layout.setAlignment(Qt.AlignLeft)

            # Add spacer item to push content to the left
            previous_layout.addWidget(number_label_previous)
            previous_layout.addWidget(previous_edit)

            # Store the previous_layout in a list
            self.previous_layouts.append(previous_layout)

            # Create and store the fields where the difference between current and previous values are shown.
            difference_label = QLabel('')
            difference_label.setStyleSheet("""
                QLabel {
                    background-color: #fff1b8;
                    color: #7a6202;
                    border: 1px solid #ccc;
                    font-family: Montserrat;
                    Font-weight:bold;
                    padding: 5px;
                    border-radius: 7px;
                }
                QLabel:hover {
                    background-color: #fff5cc;  /* Lighter green on hover */
                }
            """)
            difference_label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            difference_label.setVisible(False)
            self.difference_labels.append(difference_label)

            # Add the layouts to the grid layout
            self.grid_layout.addLayout(current_layout, i + 1, 0, 1, 2)

            # Add previous layout to grid layout
            self.grid_layout.addLayout(previous_layout, i + 1, 2, 1, 4)

            # Add the difference label (initially invisible) at the grid position
            self.grid_layout.addWidget(difference_label, i + 1, 4, 1, 1)

            # Store the input fields for later use
            self.current_labels.append(current_edit)
            self.previous_labels.append(previous_edit)
        
        # Creating a field where the amount of cash at the beginning of a day is shown
        # Aka the amount of the cash at the end of the previous day (2nd shift) is shown today.
        previous_cash_balance_label = QLabel('Prethodno stanje:')
        previous_cash_balance_label.setStyleSheet("""
            QLabel {
                background-color: #45a049;
                color: white;
                font-family: Montserrat;
                font-weight: bold;
                padding: 5px;
                padding-bottom: 6px;
                border-radius: 5px;
            }
            QLabel:hover {
                background-color: #4CAF50;  /* Lighter green on hover */
            }
        """)
        self.grid_layout.addWidget(previous_cash_balance_label, 5, 2)
        self.previous_cash_balance_label = QLineEdit(self)
        self.previous_cash_balance_label.setReadOnly(True)
        self.previous_cash_balance_label.setStyleSheet("font-family: Montserrat;font-weight:bold;font-size:14px;")
        self.grid_layout.addWidget(self.previous_cash_balance_label, 5, 3, 1, 3)
        
        # This field shows the cash balance after you calculate the new census
        current_cash_balance_label = QLabel('Trenutno stanje:')
        current_cash_balance_label.setStyleSheet("""
            QLabel {
                background-color: #45a049;
                color: white;
                font-family: Montserrat;
                font-weight: Bold;
                padding: 5px;
                border-radius: 5px;
                padding-bottom: 6px;
            }
            QLabel:hover {
                background-color: #4CAF50;  /* Lighter green on hover */
            }
        """)
        self.grid_layout.addWidget(current_cash_balance_label, 5, 0)
        self.current_cash_balance_edit = QLineEdit(self)
        self.current_cash_balance_edit.setStyleSheet("font-family: Montserrat;font-weight:bold;font-size:14px;")
        self.current_cash_balance_edit.setReadOnly(True)

        self.grid_layout.addWidget(self.current_cash_balance_edit, 5, 1)

        # This field will show the total difference between slot machines states
        self.total_slot_machines_difference_label = QLabel('Ukupna razlika aparata:')
        self.total_slot_machines_difference_label.setFixedWidth(200)
        self.total_slot_machines_difference_label.setFixedHeight(30)
        self.total_slot_machines_difference_label.setStyleSheet(
            "font-family: Montserrat;font-weight:Bold;font-size: 14px;color:green;border: 1px solid  #ccc;padding: 5px;padding-bottom:7px;background-color:white;border-radius:10px;")
        self.grid_layout.addWidget(self.total_slot_machines_difference_label, 6, 0, 1, 2)

        # Animation for `total_slot_machines_difference_label`
        self.animation_slot_machine = self.create_hover_animation(self.total_slot_machines_difference_label, 200, 260)

        self.total_slot_machines_difference_label.setMouseTracking(True)
        self.total_slot_machines_difference_label.enterEvent = lambda event: self.on_enter(
            self.total_slot_machines_difference_label, self.animation_slot_machine)
        self.total_slot_machines_difference_label.leaveEvent = lambda event: self.on_leave(
            self.total_slot_machines_difference_label, self.animation_slot_machine)

        # This field will shown the total profit or loss for the current census.
        self.total_profit_loss_label = QLabel('Ukupan profit / gubitak:')
        self.total_profit_loss_label.setStyleSheet(
            "font-family: Montserrat;font-weight:Bold;font-size: 14px;color:green;border: 1px solid  #ccc;padding: 5px;padding-bottom:7px;background-color:white;border-radius:10px;")
        self.total_profit_loss_label.setFixedWidth(200)
        self.grid_layout.addWidget(self.total_profit_loss_label, 7, 0, 1, 2)
        main_layout.addLayout(self.grid_layout)  # Dodaj self.grid_layout u glavni raspored

        # Animation for `total_profit_loss_label`
        self.animation_profit_loss = self.create_hover_animation(self.total_profit_loss_label, 200, 260)

        self.total_profit_loss_label.setMouseTracking(True)
        self.total_profit_loss_label.enterEvent = lambda event: self.on_enter(self.total_profit_loss_label,
                                                                              self.animation_profit_loss)
        self.total_profit_loss_label.leaveEvent = lambda event: self.on_leave(self.total_profit_loss_label,
                                                                              self.animation_profit_loss)

        # Hidden delete button, only shown when needed
        self.delete_button = QPushButton('', self)
        self.delete_button.setIcon(QIcon(resource_path('delete.png')))
        self.delete_button.setFixedSize(40, 40)
        self.delete_button.clicked.connect(self.delete_current_record)
        self.delete_button.setVisible(False)
        self.grid_layout.addWidget(self.delete_button, 6, 2, 0, 1)
        self.delete_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
            }
            QPushButton:hover {
            }
        """)
        self.delete_button.setIconSize(QSize(30, 30))  # Normal size
        self.delete_button.installEventFilter(self)

        # Book button for storing the short notes about today's shift if needed
        # For example if the manager took the money from the register
        self.book_button = QPushButton('', self)
        self.book_button.setIcon(QIcon(resource_path('book.png')))
        self.book_button.setFixedSize(40, 40)
        self.book_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
            }
            QPushButton:hover {
            }
        """)
        self.book_button.setIconSize(QSize(30, 30))
        self.book_button.clicked.connect(self.leave_a_message)
        self.grid_layout.addWidget(self.book_button, 6, 3, 0, 1)
        self.book_button.installEventFilter(self)

        self.notebook_button = QPushButton('', self)
        self.notebook_button.setIcon(QIcon(resource_path('notebook.png')))
        self.notebook_button.setFixedSize(40, 40)
        self.notebook_button.setStyleSheet("""
                    QPushButton {
                        background-color: transparent;
                        border: none;
                    }
                    QPushButton:hover {
                    }
                """)
        self.notebook_button.setIconSize(QSize(30, 30))
        self.notebook_button.clicked.connect(self.open_notebook)
        self.grid_layout.addWidget(self.notebook_button, 6, 4, 0, 2)
        self.notebook_button.installEventFilter(self)

        # This is the list of the deleted censuses so far, so they can be restored if needed
        self.deleted_censuses_button = QPushButton('', self)
        self.deleted_censuses_button.setIcon(QIcon(resource_path('deleted_censuses.png')))
        self.deleted_censuses_button.setFixedSize(40, 40)
        self.deleted_censuses_button.setStyleSheet("""
                            QPushButton {
                                background-color: transparent;
                                border: none;
                            }
                            QPushButton:hover {
                            }
                        """)
        self.deleted_censuses_button.setIconSize(QSize(30, 30))
        self.deleted_censuses_button.clicked.connect(self.prikazi_obrisane_popise)
        self.grid_layout.addWidget(self.deleted_censuses_button, 6, 4, 0, 2)
        self.deleted_censuses_button.installEventFilter(self)
        self.deleted_censuses_button.setVisible(False)

        label_handed = QLabel("Ukupno predato:")
        label_handed.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        label_handed.setStyleSheet("""
            QLabel {
                background-color: #4CAF50;
                color: white;
                font-family: Montserrat;
                font-weight: bold;
                padding: 5px;
                padding-bottom: 7px;
                border-radius: 5px;
            }
            QLabel:hover {
                background-color: #45a049;  /* Lighter green on hover */
            }
        """)
        self.grid_layout.addWidget(label_handed, 7, 2)
        self.handed_input = QLineEdit()
        self.handed_input.setStyleSheet("font-family: Montserrat;font-weight:Bold;font-size:14px;")
        self.grid_layout.addWidget(self.handed_input, 7, 3, 1, 3)

        group_layout = QVBoxLayout()
        group_labels = ["BG", "KL", "LV"]
        self.group_edits = []

        for label_text in group_labels:
            h_layout = QHBoxLayout()

            # Create the label and apply styles
            label = QLabel(label_text)
            label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            label.setFixedSize(38, 32)
            label.setStyleSheet("""
                    QLabel {
                        background-color: #45a049;
                        color: white;
                        font-size: 14px;
                        font-family: Montserrat;
                        font-weight:bold;
                        font-style: italic;
                        padding: 5px;
                        border-radius: 5px;
                    }
                    QLabel:hover {
                        background-color: #4CAF50;  /* Lighter green on hover */
                    }
                """)
            h_layout.addWidget(label)

            # Create the input field
            group_edit = CustomLineEditZ(self)
            group_edit.setStyleSheet("font-family: Montserrat;Font-weight:bold;font-size:14px;")
            h_layout.addWidget(group_edit)

            # Add the input field to the list
            self.group_edits.append(group_edit)

            # Add the horizontal layout to the main layout
            group_layout.addLayout(h_layout)

        # Add group_layout to the main layout
        main_layout.addLayout(group_layout)

        # Action buttons with modern icons and styles
        button_layout = QHBoxLayout()

        self.calculate_btn = QPushButton('IZRAČUNAJ', self)
        self.calculate_btn.setStyleSheet('''
                        font-size: 11px;
                        font-family: Montserrat;
                        font-weight:bold;
                        font-style: italic;
                        ''')
        self.calculate_btn.clicked.connect(self.calculate)
        self.calculate_btn.installEventFilter(self)
        button_layout.addWidget(self.calculate_btn)

        self.save_btn = QPushButton('SAČUVAJ', self)
        self.save_btn.setStyleSheet('''
                        font-size: 11px;
                        font-family: Montserrat;
                        font-weight:bold;
                        font-style: italic;
                        ''')
        self.save_button_reconnect()
        button_layout.addWidget(self.save_btn)

        search_btn = QPushButton('', self)  # Empty string for text, uses icon
        search_btn.setIcon(QIcon(resource_path('calendar.png')))  # Icon for the calendar picker
        search_btn.setFixedSize(40, 40)
        search_btn.clicked.connect(self.show_date_picker)
        button_layout.addWidget(search_btn)
        search_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
            }
            QPushButton:hover {
            }
        """)
        search_btn.setIconSize(QSize(30, 30))  # Normal size
        search_btn.installEventFilter(self)

        # Creating a button for setting the new previous states
        new_initial_state_btn = QPushButton('', self)
        new_initial_state_btn.setIcon(QIcon(resource_path('documentation.png')))
        new_initial_state_btn.setFixedSize(40, 40)
        new_initial_state_btn.clicked.connect(self.set_new_initial_state)
        button_layout.addWidget(new_initial_state_btn)
        new_initial_state_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
            }
            QPushButton:hover {
            }
        """)
        new_initial_state_btn.setIconSize(QSize(30, 30))  # Normal size
        new_initial_state_btn.installEventFilter(self)

        # This button allows user to see previous census
        back_btn = QPushButton('PRETHODNI POPIS', self)
        back_btn.setStyleSheet('''
                        font-size: 11px;
                        font-family: Montserrat;
                        font-weight:bold;
                        font-style: italic;
                        ''')
        back_btn.clicked.connect(self.load_previous_record)
        button_layout.addWidget(back_btn)

        # This button allows user to see next census
        next_btn = QPushButton('NAREDNI POPIS', self)
        next_btn.setStyleSheet('''
                        font-size: 11px;
                        font-family: Montserrat;
                        font-weight:bold;
                        font-style: italic;
                        ''')
        next_btn.clicked.connect(self.load_next_record)
        button_layout.addWidget(next_btn)

        # Adding lower layout where buttons are located to the main layout
        main_layout.addLayout(button_layout)

        # Showing the main layout
        self.setLayout(main_layout)
        self.setWindowTitle(' Popis Kladionice')
        self.show()

        self.delete_button.setVisible(False)  # Hide delete button initially
        self.saved_message = ""


    # Creating a function to make icons larger on hover
    def eventFilter(self, obj, event):
        if isinstance(obj, QPushButton) and event.type() == QEvent.Enter:
            obj.setIconSize(QSize(40, 40))  # Larger icon on hover
        elif isinstance(obj, QPushButton) and event.type() == QEvent.Leave:
            obj.setIconSize(QSize(30, 30))  # Revert to normal icon size when hover ends
        return super().eventFilter(obj, event)

    # This function populates the main layout with the components
    # from the last census when the program is started.
    def load_previous_state(self):
        # Filter the results for "Druga smena" and sort it by id, desc
        state = session.query(slotMachineState).filter(slotMachineState.smena == "Druga smena").order_by(
            desc(slotMachineState.datum), desc(slotMachineState.id)).first()

        if state:
            self.previous_labels[0].setText(str(state.slot_machine_1))
            self.previous_labels[1].setText(str(state.slot_machine_2))
            self.previous_labels[2].setText(str(state.slot_machine_3))
            self.previous_labels[3].setText(str(state.slot_machine_4))
            self.previous_cash_balance_label.setText(str(state.cash_balance))
        else:
            # if there are no results for "Druga smena", set everything to "0".
            for label in self.previous_labels:
                label.setText('0')
            self.previous_cash_balance_label.setText('0')
    
    
    # This function will calculate our census with given data.
    def calculate(self):
        try:
            # initialising starting values.
            total_profit_loss = 0
            total_slot_machines_difference = 0
            
            # calculating the difference between previous and current values
            for i in range(4):
                previous_value = int(self.previous_labels[i].text())
                current_value = self.current_labels[i].text()

                # To make it easier for the employees, if they leave the space empty
                # by pressing the space button, the previous value will be
                # copied to current value.
                if str(current_value) == "":
                    current_value = previous_value
                    self.current_labels[i].setText(str(previous_value))
                else:
                    current_value = int(current_value)

                difference = current_value - previous_value

                total_slot_machines_difference += difference
                
                # Setting the value for each difference_label
                self.difference_labels[i].setText(str(difference))

            # including handed_values to the equation
            handed_value = self.handed_input.text()
            if handed_value == "":
                handed_value = 0
            else:
                handed_value = int(self.handed_input.text())

            # To make it easier for the users, if any of the fields in group edits,
            # Are left empty, their value will just be set to 0
            for i in range(3):
                if self.group_edits[i].text() == "":
                    self.group_edits[i].setText("0")
            group_ticket = int(self.group_edits[0].text())
            group_bingo = int(self.group_edits[1].text())
            group_live = int(self.group_edits[2].text())

            # Calculating total profit since yesterday
            total_profit_loss += group_ticket + group_bingo + group_live + total_slot_machines_difference + handed_value

            previous_cash_balance = int(self.previous_cash_balance_label.text())

            # Setting the value of current cash balance
            current_cash_balance = previous_cash_balance + total_profit_loss
            self.current_cash_balance_edit.setText(str(current_cash_balance))

            # Setting the value for other labels
            self.total_profit_loss_label.setText(f'Ukupan profit / gubitak: {total_profit_loss}')
            self.total_slot_machines_difference_label.setText(f'Ukupna razlika aparata: {total_slot_machines_difference}')

            # Starting the animation after the "Izračunaj" button has be pressed
            self.on_enter(self.total_slot_machines_difference_label, self.animation_slot_machine)
            self.on_enter(self.total_profit_loss_label, self.animation_profit_loss)

            # Making sure that the fields remain stretched
            QTimer.singleShot(320, lambda: self.total_slot_machines_difference_label.setFixedWidth(260))
            QTimer.singleShot(320, lambda: self.total_profit_loss_label.setFixedWidth(260))

            for i, previous_layout in enumerate(self.previous_layouts):
                # Remove any existing spacers at the end
                item_count = previous_layout.count()
                if item_count > 2:  # Assuming there's a spacer at index 2
                    item = previous_layout.takeAt(2)
                    if item.spacerItem():
                        previous_layout.removeItem(item)

                # Make the difference label visible
                self.difference_labels[i].setVisible(True)

                # Add a spacer to ensure distance between previous_edit and difference_label
                spacer_between = QSpacerItem(0, 20, QSizePolicy.Fixed, QSizePolicy.Minimum)
                previous_layout.addItem(spacer_between)

                # Add the difference label to the layout
                previous_layout.addWidget(self.difference_labels[i])
                self.previous_labels[i].setFixedWidth(170)

            try:
                self.compare_with_saved_state()  # Call the function from the parent class
            except Exception:
                pass
        except ValueError:
            if str(self.current_labels[0].text().lower()) == "obrad":
                QMessageBox.information(self, 'Tajne odaje', 'Program napravio Obrad Ružičić.')
            else:
                QMessageBox.warning(self, 'Greška', 'Molimo unesite validna stanja pre računanja.')

    from datetime import datetime

    def get_differences(self, current_state, saved_state):
        differences = {}
        for attr in vars(current_state):
            if attr.startswith('_'):
                continue  # Skip SQLAlchemy internal attributes

            current_value = getattr(current_state, attr)
            saved_value = getattr(saved_state, attr, None)

            # Special handling for 'datum' field to only compare dates
            if attr == 'datum' and isinstance(current_value, datetime) and isinstance(saved_value, datetime):
                if current_value.date() != saved_value.date():
                    differences[attr] = {'saved': saved_value, 'current': current_value}
            else:
                if current_value != saved_value:
                    differences[attr] = {'saved': saved_value, 'current': current_value}

        return differences

    def save_current_state(self):

        try:

            # Unos podataka
            slot_machine_1 = int(self.current_labels[0].text())
            slot_machine_2 = int(self.current_labels[1].text())
            slot_machine_3 = int(self.current_labels[2].text())
            slot_machine_4 = int(self.current_labels[3].text())
            cash_balance = int(self.current_cash_balance_edit.text())
            group_ticket = int(self.group_edits[0].text())
            group_bingo = int(self.group_edits[1].text())
            group_live = int(self.group_edits[2].text())
            previous_difference_1 = int(self.difference_labels[0].text())
            previous_difference_2 = int(self.difference_labels[1].text())
            previous_difference_3 = int(self.difference_labels[2].text())
            previous_difference_4 = int(self.difference_labels[3].text())

            saved_message = self.saved_message

            # Changing shift and date to yesterday's if necessary
            if self.changed == True:
                shift = "Druga smena"
                date = self.yesterday

            # Saving the current date and shift depending on what time it is
            else:
                current_time = datetime.now().time()
                if current_time < datetime.strptime("18:00", "%H:%M").time():
                    shift = "Prva smena"
                    date = datetime.now()
                else:
                    shift = "Druga smena"
                    date = datetime.now()

            # Saving the monthly states
            monthly_slot_machine_1 = int(self.slot_machine_1_monthly_pass)
            monthly_slot_machine_2 = int(self.slot_machine_2_monthly_pass)
            monthly_slot_machine_3 = int(self.slot_machine_3_monthly_pass)
            monthly_slot_machine_4 = int(self.slot_machine_4_monthly_pass)

            # Preparing the new census
            new_state = slotMachineState(
                slot_machine_1=slot_machine_1,
                slot_machine_2=slot_machine_2,
                slot_machine_3=slot_machine_3,
                slot_machine_4=slot_machine_4,
                cash_balance=cash_balance,
                group_ticket=group_ticket,
                group_bingo=group_bingo,
                group_live=group_live,
                total_profit_loss=int(self.total_profit_loss_label.text().split(': ')[1]),
                total_slot_machines_difference=int(self.total_slot_machines_difference_label.text().split(': ')[1]),
                previous_slot_machine_1=int(self.previous_labels[0].text()),
                previous_slot_machine_2=int(self.previous_labels[1].text()),
                previous_slot_machine_3=int(self.previous_labels[2].text()),
                previous_slot_machine_4=int(self.previous_labels[3].text()),
                previous_cash_balance=int(self.previous_cash_balance_label.text()),
                datum=date,
                smena=shift,
                previous_difference_1=previous_difference_1,
                previous_difference_2=previous_difference_2,
                previous_difference_3=previous_difference_3,
                previous_difference_4=previous_difference_4,
                monthly_slot_machine_1=monthly_slot_machine_1,
                monthly_slot_machine_2=monthly_slot_machine_2,
                monthly_slot_machine_3=monthly_slot_machine_3,
                monthly_slot_machine_4=monthly_slot_machine_4,
                message_list=saved_message,
            )

            # Compare with the saved state if it exists
            if self.saved_state:
                differences = self.get_differences(new_state, self.saved_state)
                if differences:
                    self.save_btn.setStyleSheet('''
                                    QPushButton {
                                        background-color: #4CAF50;
                                        color: white;
                                        border: none;
                                        font-size: 11px;
                                        font-family: Montserrat;
                                        font-weight:bold;
                                        font-style: italic;
                                    }
                                    QPushButton:hover {
                                        background-color: #45a049;
                                    }
                                    ''')
                    self.save_btn.setText("SAČUVAJ")

                    self.save_btn.clicked.disconnect()
                    self.save_btn.clicked.connect(self.save_current_state)
                else:
                    self.save_btn.setStyleSheet('''
                                    QPushButton {
                                        background-color: #fff1b8;
                                        color: #7a6202;
                                        border: 1px solid #ccc;
                                        font-size: 11px;
                                        font-family: Montserrat;
                                        font-weight:bold;
                                        font-style: italic;

                                    }
                                    QPushButton:hover {
                                        background-color: #fff5cc;  /* Lighter green on hover */
                                    }''')
                    self.save_btn.setText("SAČUVANO")
                    self.save_btn.clicked.disconnect()
                    self.save_btn.clicked.connect(self.already_saved)

            # Update the saved state
            self.saved_state = new_state

            # Save to the database
            session.add(new_state)
            session.commit()

            self.save_btn.setStyleSheet('''
               QPushButton {
                   background-color: #fff1b8;
                   color: #7a6202;
                   border: 1px solid #ccc;
                   font-size: 11px;
                   font-family: Montserrat;
                   font-weight:bold;
                   font-style: italic;

               }
               QPushButton:hover {
                   background-color: #fff5cc;  /* Lighter green on hover */
               }''')
            self.save_btn.setText("SAČUVANO")
            self.save_btn.clicked.disconnect()
            self.save_btn.clicked.connect(self.already_saved)
            QMessageBox.information(self, 'Uspeh', 'Podaci su uspešno sačuvani.')

        except ValueError as e:
            QMessageBox.warning(self, 'Greška', 'Molimo unesite validna stanja za sve aparate i kladionicu.')
            print(e)

        except Exception as e:
            QMessageBox.critical(self, 'Greška', f"Došlo je do greške prilikom čuvanja podataka: {e}")

    # Make sure that user can't use save button while reviewing history
    def save_button_reconnect(self):
        if self.is_reviewing_history:
            self.save_btn.clicked.disconnect()
            self.save_btn.clicked.connect(self.information)
        else:
            self.save_btn.clicked.connect(self.save_current_state)

    def compare_with_saved_state(self):

        if not hasattr(self, 'saved_state'):
            return  # If no state has been saved yet, exit

            # Create a new state with the current values
        current_state = slotMachineState(
            slot_machine_1=int(self.current_labels[0].text()),
            slot_machine_2=int(self.current_labels[1].text()),
            slot_machine_3=int(self.current_labels[2].text()),
            slot_machine_4=int(self.current_labels[3].text()),
            cash_balance=int(self.current_cash_balance_edit.text()),
            group_ticket=int(self.group_edits[0].text()),
            group_bingo=int(self.group_edits[1].text()),
            group_live=int(self.group_edits[2].text()),
            total_profit_loss=int(self.total_profit_loss_label.text().split(': ')[1]),
            total_slot_machines_difference=int(self.total_slot_machines_difference_label.text().split(': ')[1]),
            previous_slot_machine_1=int(self.previous_labels[0].text()),
            previous_slot_machine_2=int(self.previous_labels[1].text()),
            previous_slot_machine_3=int(self.previous_labels[2].text()),
            previous_slot_machine_4=int(self.previous_labels[3].text()),
            previous_cash_balance=int(self.previous_cash_balance_label.text()),
            previous_difference_1=int(self.difference_labels[0].text()),
            previous_difference_2=int(self.difference_labels[1].text()),
            previous_difference_3=int(self.difference_labels[2].text()),
            previous_difference_4=int(self.difference_labels[3].text()),
            monthly_slot_machine_1=int(self.slot_machine_1_monthly_pass),
            monthly_slot_machine_2=int(self.slot_machine_2_monthly_pass),
            monthly_slot_machine_3=int(self.slot_machine_3_monthly_pass),
            monthly_slot_machine_4=int(self.slot_machine_4_monthly_pass),
            message_list=self.saved_message
        )


        # Compare the current state with the saved state
        if self.saved_state:
            differences = self.get_differences(current_state, self.saved_state)
            if differences:
                # Update save button to indicate unsaved changes
                self.save_btn.setStyleSheet('''
                                        QPushButton {
                                            background-color: #4CAF50;
                                            color: white;
                                            border: none;
                                            font-size: 11px;
                                            font-family: Montserrat;
                                            font-weight:bold;
                                            font-style: italic;
                                        }
                                        QPushButton:hover {
                                            background-color: #45a049;
                                        }
                                        ''')
                self.save_btn.setText("SAČUVAJ")

                self.save_btn.clicked.disconnect()
                self.save_btn.clicked.connect(self.save_current_state)
            else:
                # Update save button to indicate no changes
                self.save_btn.setStyleSheet('''
                                        QPushButton {
                                            background-color: #fff1b8;
                                            color: #7a6202;
                                            border: 1px solid #ccc;
                                            font-size: 11px;
                                            font-family: Montserrat;
                                            font-weight:bold;
                                            font-style: italic;

                                        }
                                        QPushButton:hover {
                                            background-color: #fff5cc;
                                        }''')
                self.save_btn.setText("SAČUVANO")
                self.save_btn.clicked.disconnect()
                self.save_btn.clicked.connect(self.already_saved)
    def leave_a_message(self):
        note = QDialog(self)
        note.setWindowTitle("Zapisnik")
        note.setFixedSize(400, 260)
        note.setWindowFlags(note.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        self.new_note = QTextEdit(note)
        self.new_note.setPlaceholderText("Unesite poruku...")
        self.new_note.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.new_note.setStyleSheet("""
                QTextEdit {
                    font-family: Montserrat;
                    font-weight: bold;
                    font-size: 14px;
                    border: 3px solid black;
                    border-radius: 10px;
                    padding: 5px;
                }
            """)

        if self.red_set == True:
            self.new_note.setText(self.saved_message)

        ok_button = QPushButton('SAČUVAJ', note)
        ok_button.setStyleSheet('font-family: Montserrat; font-weight: bold; font-style: italic;')

        button_layout = QHBoxLayout()
        button_layout.addWidget(ok_button)
        ok_button.setFixedWidth(374)
        ok_button.clicked.connect(lambda: self.save_message(self.new_note.toPlainText()))

        button_layout.addStretch()
        if self.is_reviewing_history:
            try:
                self.new_note.setText(str(self.records[self.current_record_index].message_list))
                self.new_note.setReadOnly(True)
                ok_button.setVisible(False)
            except Exception as e:
                print(e)

        layout = QFormLayout(note)
        layout.addRow(self.new_note)
        layout.addRow(button_layout)
        note.setLayout(layout)

        note.exec_()

    def print_saved_state_attributes(self):
        if self.saved_state:
            print("Attributes and their types in saved_state:")
            for attr, value in self.saved_state.__dict__.items():
                print(f"{attr}: {type(value)}")

    def open_notebook(self):
        layout = QVBoxLayout()  # This remains to organize everything vertically

        notebook = QDialog(self)
        notebook.setWindowTitle("Nedeljni popis")
        notebook.setFixedSize(300, 80)
        notebook.setWindowFlags(notebook.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        edit_states = QPushButton('PROMENI STANJA', notebook)
        edit_states.setStyleSheet('font-family: Montserrat; font-weight: bold; font-style: italic;')
        edit_states.clicked.connect(self.notebook_edit_states)

        copy_states = QPushButton('KOPIRAJ STANJA', notebook)
        copy_states.setStyleSheet('font-family: Montserrat; font-weight: bold; font-style: italic;')
        copy_states.clicked.connect(self.copy_notebook_states)

        button_layout = QHBoxLayout()  # Use QHBoxLayout to align buttons horizontally
        button_layout.addWidget(edit_states)
        button_layout.addWidget(copy_states)

        layout.addLayout(button_layout)  # Add horizontal layout to the main vertical layout

        notebook.setLayout(layout)
        notebook.exec_()

    def notebook_edit_states(self):
        try:
            e_layout = QFormLayout()
            e_dialog = QDialog()
            e_dialog.setWindowIcon(QIcon(resource_path('logo.png')))
            e_dialog.setStyleSheet("""
                        QWidget {
                            background-color: white;
                        }
                        QLabel {
                            font-size: 14px;
                            color: #333;
                        }
                        QLineEdit {
                            background-color: #f0f0f0;
                            border: 1px solid #ccc;
                            padding: 5px;
                            border-radius: 5px;
                        }
                        QLineEdit:hover {
                            border: 2px solid #4CAF50;
                        }
                        QLineEdit:focus {
                            border: 2px solid #4CAF50;  /* Highlight with green border */
                            background-color: #e0ffe0;  /* Slightly different background when focused */
                        }
                        QPushButton {
                            font-weight: bold;
                            background-color: #4CAF50;
                            color: white;
                            border-radius: 10px;
                            padding: 5px;
                            border: none;
                        }
                        QPushButton:hover {
                            background-color: #45a049;
                        }
                    """)
            e_dialog.setWindowTitle("Promena stanja")
            e_dialog.setFixedSize(300, 200)
            e_dialog.setWindowFlags(e_dialog.windowFlags() & ~Qt.WindowContextHelpButtonHint)

            self.slot_machine_1_monthly = CustomLineEdit(e_dialog)
            self.slot_machine_1_monthly.setStyleSheet("font-family: Montserrat;Font-weight:bold;font-size:14px;")
            self.slot_machine_1_monthly.setText(str(self.slot_machine_1_monthly_pass))

            self.slot_machine_2_monthly = CustomLineEdit(e_dialog)
            self.slot_machine_2_monthly.setStyleSheet("font-family: Montserrat;Font-weight:bold;font-size:14px;")
            self.slot_machine_2_monthly.setText(str(self.slot_machine_2_monthly_pass))

            self.slot_machine_3_monthly = CustomLineEdit(e_dialog)
            self.slot_machine_3_monthly.setStyleSheet("font-family: Montserrat;Font-weight:bold;font-size:14px;")
            self.slot_machine_3_monthly.setText(str(self.slot_machine_3_monthly_pass))

            self.slot_machine_4_monthly = CustomLineEdit(e_dialog)
            self.slot_machine_4_monthly.setStyleSheet("font-family: Montserrat;Font-weight:bold;font-size:14px;")
            self.slot_machine_4_monthly.setText(str(self.slot_machine_4_monthly_pass))
        except Exception as e:
            print(e)

        try:
            # Creating QLabel elements for each number and cash_balanceP
            new_number = QLabel('1')
            new_number.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            new_number.setFixedWidth(40)
            new_number.setStyleSheet("""
                QLabel {
                    background-color: #45a049;
                    color: white;
                    font-family: Montserrat Black;
                    padding: 5px;
                    border-radius: 5px;
                }
                QLabel:hover {
                    background-color: #4CAF50;  /* Lighter green on hover */
                }
            """)
            new_number2 = QLabel('2')
            new_number2.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            new_number2.setFixedWidth(40)
            new_number2.setStyleSheet("""
                QLabel {
                    background-color: #45a049;
                    color: white;
                    font-family: Montserrat Black;
                    font-style: italic;
                    padding: 5px;
                    border-radius: 5px;
                }
                QLabel:hover {
                    background-color: #4CAF50;  /* Lighter green on hover */
                }
            """)

            new_number3 = QLabel('3')
            new_number3.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            new_number3.setFixedWidth(40)
            new_number3.setStyleSheet("""
                QLabel {
                    background-color: #45a049;
                    color: white;
                    font-family: Montserrat Black;
                    font-style: italic;
                    padding: 5px;
                    border-radius: 5px;
                }
                QLabel:hover {
                    background-color: #4CAF50;  /* Lighter green on hover */
                }
            """)

            new_number4 = QLabel('4')
            new_number4.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            new_number4.setFixedWidth(40)
            new_number4.setStyleSheet("""
                QLabel {
                    background-color: #45a049;
                    color: white;
                    font-family: Montserrat Black;
                    font-style: italic;
                    padding: 5px;
                    border-radius: 5px;
                }
                QLabel:hover {
                    background-color: #4CAF50;  /* Lighter green on hover */
                }
            """)

            # ... similar setup for new_number2, new_number3, new_number4, new_cash_balanceP

            e_layout.addRow(new_number, self.slot_machine_1_monthly)
            e_layout.addRow(new_number2, self.slot_machine_2_monthly)
            e_layout.addRow(new_number3, self.slot_machine_3_monthly)
            e_layout.addRow(new_number4, self.slot_machine_4_monthly)
        except Exception as e:
            print(e)
        try:
            ok_button = QPushButton('POTVRDI', e_dialog)
            ok_button.setStyleSheet('font-family: Montserrat; font-weight: bold; font-style: italic;')
            ok_button.clicked.connect(self.save_notebook_states)

            button_layout = QHBoxLayout()
            button_layout.addWidget(ok_button)
            ok_button.setFixedWidth(275)

            # Add stretch to make the button take full width
            button_layout.addStretch()

            e_layout.addRow(button_layout)
            e_dialog.setLayout(e_layout)
            e_dialog.exec_()
        except Exception as e:
            print(e)

    def pass_notebook_states(self):
        state = session.query(slotMachineState).order_by(
            desc(slotMachineState.datum), desc(slotMachineState.id)).first()
        try:

            if state:

                self.slot_machine_1_monthly_pass = str(state.monthly_slot_machine_1)
                self.slot_machine_2_monthly_pass = str(state.monthly_slot_machine_2)
                self.slot_machine_3_monthly_pass = str(state.monthly_slot_machine_3)
                self.slot_machine_4_monthly_pass = str(state.monthly_slot_machine_4)
            else:
                # Ako nema rezultata za drugu smenu, postavi sve na '0'

                self.slot_machine_1_monthly_pass = "0"
                self.slot_machine_2_monthly_pass = "0"
                self.slot_machine_3_monthly_pass = "0"
                self.slot_machine_4_monthly_pass = "0"
        except Exception as e:
            print(e)

    def save_notebook_states(self):
        try:
            records = session.query(slotMachineState).order_by(slotMachineState.datum).all()
            menjaza = records[-1]
            menjaza.monthly_slot_machine_1 = int(self.slot_machine_1_monthly.text())
            menjaza.monthly_slot_machine_2 = int(self.slot_machine_2_monthly.text())
            menjaza.monthly_slot_machine_3 = int(self.slot_machine_3_monthly.text())
            menjaza.monthly_slot_machine_4 = int(self.slot_machine_4_monthly.text())
            session.commit()

            self.slot_machine_1_monthly_pass = int(self.slot_machine_1_monthly.text())
            self.slot_machine_2_monthly_pass = int(self.slot_machine_2_monthly.text())
            self.slot_machine_3_monthly_pass = int(self.slot_machine_3_monthly.text())
            self.slot_machine_4_monthly_pass = int(self.slot_machine_4_monthly.text())


        except Exception as e:
            print(e)

        QMessageBox.information(self, 'Uspeh', 'Stanja su uspešno ažurirana.')

    def copy_notebook_states(self):
        self.previous_labels[0].setText(str(self.slot_machine_1_monthly_pass))
        self.previous_labels[1].setText(str(self.slot_machine_2_monthly_pass))
        self.previous_labels[2].setText(str(self.slot_machine_3_monthly_pass))
        self.previous_labels[3].setText(str(self.slot_machine_4_monthly_pass))

        self.save_btn.disconnect()
        self.save_btn.clicked.connect(self.information)
        QMessageBox.information(self, 'Uspeh', 'Stanja su uspešno prekopirana.')

    def save_message(self, x):
        try:
            self.saved_message = x
            QMessageBox.information(self, 'Uspeh', 'Poruka je uspešno sačuvana.')
            self.book_button.setIcon(QIcon(resource_path('book_red.png')))
            self.new_note.setText(self.saved_message)
            self.new_note.parent().accept()  # Zatvara dijalog nakon čuvanja
            self.red_set = True
            self.compare_with_saved_state()


        except Exception:
            QMessageBox.warning(self, 'Greška', 'Došlo je do greške.')

    def set_new_initial_state(self):
        dialog = QDialog(self)
        dialog.setWindowTitle('Promena početnog stanja')
        dialog.setFixedSize(300, 230)
        dialog.setWindowFlags(dialog.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        layout = QFormLayout(dialog)
        #vamo

        # Unos za aparate
        self.new_slot_machine_1_input = CustomLineEdit(dialog)
        self.new_slot_machine_1_input.setStyleSheet("font-family: Montserrat;Font-weight:bold;font-size:14px;")

        self.new_slot_machine_2_input = CustomLineEdit(dialog)
        self.new_slot_machine_2_input.setStyleSheet("font-family: Montserrat;Font-weight:bold;font-size:14px;")

        self.new_slot_machine_3_input = CustomLineEdit(dialog)
        self.new_slot_machine_3_input.setStyleSheet("font-family: Montserrat;Font-weight:bold;font-size:14px;")

        self.new_slot_machine_4_input = CustomLineEdit(dialog)
        self.new_slot_machine_4_input.setStyleSheet("font-family: Montserrat;Font-weight:bold;font-size:14px;")

        self.new_cash_balance_input = CustomLineEdit(dialog)
        self.new_cash_balance_input.setStyleSheet("font-family: Montserrat;Font-weight:bold;font-size:14px;")

        try:
            # Creating QLabel elements for each number and cash_balanceP
            new_number = QLabel('1')
            new_number.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            new_number.setFixedWidth(50)
            new_number.setStyleSheet("""
                QLabel {
                    background-color: #45a049;
                    color: white;
                    font-family: Montserrat Black;
                    padding: 5px;
                    border-radius: 5px;
                }
                QLabel:hover {
                    background-color: #4CAF50;  /* Lighter green on hover */
                }
            """)
            new_number2 = QLabel('2')
            new_number2.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            new_number2.setFixedWidth(50)
            new_number2.setStyleSheet("""
                QLabel {
                    background-color: #45a049;
                    color: white;
                    font-family: Montserrat Black;
                    font-style: italic;
                    padding: 5px;
                    border-radius: 5px;
                }
                QLabel:hover {
                    background-color: #4CAF50;  /* Lighter green on hover */
                }
            """)

            new_number3 = QLabel('3')
            new_number3.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            new_number3.setFixedWidth(50)
            new_number3.setStyleSheet("""
                QLabel {
                    background-color: #45a049;
                    color: white;
                    font-family: Montserrat Black;
                    font-style: italic;
                    padding: 5px;
                    border-radius: 5px;
                }
                QLabel:hover {
                    background-color: #4CAF50;  /* Lighter green on hover */
                }
            """)

            new_number4 = QLabel('4')
            new_number4.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            new_number4.setFixedWidth(50)
            new_number4.setStyleSheet("""
                QLabel {
                    background-color: #45a049;
                    color: white;
                    font-family: Montserrat Black;
                    font-style: italic;
                    padding: 5px;
                    border-radius: 5px;
                }
                QLabel:hover {
                    background-color: #4CAF50;  /* Lighter green on hover */
                }
            """)

            new_cash_balanceP = QLabel('KASA')
            new_cash_balanceP.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            new_cash_balanceP.setFixedWidth(50)
            new_cash_balanceP.setStyleSheet("""
                QLabel {
                    background-color: #45a049;
                    color: white;
                    font-size:13px;
                    font-family: Montserrat;
                    font-weight: bold;
                    font-style: italic;
                    padding: 5px;
                    border-radius: 5px;
                }
                QLabel:hover {
                    background-color: #4CAF50;  /* Lighter green on hover */
                }
            """)

            # ... similar setup for new_number2, new_number3, new_number4, new_cash_balanceP

            layout.addRow(new_number, self.new_slot_machine_1_input)
            layout.addRow(new_number2, self.new_slot_machine_2_input)
            layout.addRow(new_number3, self.new_slot_machine_3_input)
            layout.addRow(new_number4, self.new_slot_machine_4_input)
            layout.addRow(new_cash_balanceP, self.new_cash_balance_input)
        except Exception as e:
            print(e)

        # Make the OK button wide
        ok_button = QPushButton('POTVRDI', dialog)
        ok_button.setStyleSheet('font-family: Montserrat; font-weight: bold; font-style: italic;')

        # Create a QHBoxLayout to make the button wide
        button_layout = QHBoxLayout()
        button_layout.addWidget(ok_button)
        ok_button.setFixedWidth(275)

        # Add stretch to make the button take full width
        button_layout.addStretch()

        ok_button.clicked.connect(lambda: self.save_new_initial_state(dialog))

        if self.is_reviewing_history:
            ok_button.clicked.disconnect()
            ok_button.clicked.connect(self.information)
        # Add the button layout to the form layout
        layout.addRow(button_layout)
        dialog.setLayout(layout)
        dialog.exec_()

    def information(self):
        QMessageBox.information(self, 'Greška', 'Trenutno ne možete izvršiti ovu radnju.')

    def already_saved(self):
        QMessageBox.information(self, 'Greška', 'Već ste sačuvali ovaj popis.')



    def show_date_picker(self):
        # Kreiramo novi dijalog sa kalendarom za odabir datuma
        dialog = QDialog(self)
        dialog.setWindowTitle("Izaberite datum")
        dialog.setStyleSheet("color:black;")
        dialog.setWindowFlags(dialog.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        layout = QVBoxLayout(dialog)
        calendar = QCalendarWidget(dialog)
        layout.addWidget(calendar)

        # Dodajemo dugme za potvrdu
        ok_button = QPushButton('POTVRDI', dialog)
        ok_button.setStyleSheet('font-family: Montserrat; font-weight: bold;font-style:italic;'
                                'color:white')
        ok_button.clicked.connect(lambda: self.search_by_date(calendar.selectedDate(), dialog))
        layout.addWidget(ok_button)

        dialog.setLayout(layout)
        dialog.exec_()

    def search_by_date(self, qdate, dialog):
        # Konvertovanje PyQt datuma u Python datetime
        selected_date = qdate.toPyDate()
        states = session.query(slotMachineState).filter(slotMachineState.datum.between(
            datetime.combine(selected_date, datetime.min.time()),
            datetime.combine(selected_date, datetime.max.time())
        )).all()
        dialog.close()
        if states:
            self.show_records_for_date(states)
        else:
            QMessageBox.warning(self, 'Greška', f'Nema zapisa za datum {selected_date}.')

    def show_records_for_date(self, states):
        """Prikazuje podatke za izabrani datum."""
        self.records = sorted(states, key=lambda state: state.datum,
                              reverse=True)  # Sortiramo od najnovijeg ka najstarijem
        self.current_record_index = 0
        self.is_reviewing_history = True
        self.populate_record(self.records[self.current_record_index])
        self.save_button_reconnect()

    def populate_record(self, state):
        """Popunjava UI sa podacima iz baze."""
        if str(self.records[self.current_record_index].message_list) != "":
            self.book_button.setIcon(QIcon(resource_path('book_red.png')))
        else:
            self.book_button.setIcon(QIcon(resource_path('book.png')))

        self.current_labels[0].setText(str(state.slot_machine_1))
        self.current_labels[1].setText(str(state.slot_machine_2))
        self.current_labels[2].setText(str(state.slot_machine_3))
        self.current_labels[3].setText(str(state.slot_machine_4))
        self.current_cash_balance_edit.setText(str(state.cash_balance))

        self.previous_labels[0].setText(str(state.previous_slot_machine_1))
        self.previous_labels[1].setText(str(state.previous_slot_machine_2))
        self.previous_labels[2].setText(str(state.previous_slot_machine_3))
        self.previous_labels[3].setText(str(state.previous_slot_machine_4))
        self.previous_cash_balance_label.setText(str(state.previous_cash_balance))

        self.group_edits[0].setText(str(state.group_ticket))
        self.group_edits[1].setText(str(state.group_bingo))
        self.group_edits[2].setText(str(state.group_live))

        self.difference_labels[0].setText(str(state.previous_difference_1))
        self.difference_labels[1].setText(str(state.previous_difference_2))
        self.difference_labels[2].setText(str(state.previous_difference_3))
        self.difference_labels[3].setText(str(state.previous_difference_4))
        self.date_label.setText(f'{state.datum.strftime("%d-%m-%Y")} - {state.smena}')

        self.total_profit_loss_label.setText(f'Ukupan profit / gubitak: {state.total_profit_loss}')
        self.total_slot_machines_difference_label.setText(f'Ukupna razlika aparata: {state.total_slot_machines_difference}')

        if state.smena == "Prva smena":
            self.change_shift_button.setVisible(True)
        else:
            self.change_shift_button.setVisible(False)

    def save_new_initial_state(self,dialog):
        try:
            # Preuzimanje novih početnih stanja
            new_slot_machine_1 = int(self.new_slot_machine_1_input.text())
            new_slot_machine_2 = int(self.new_slot_machine_2_input.text())
            new_slot_machine_3 = int(self.new_slot_machine_3_input.text())
            new_slot_machine_4 = int(self.new_slot_machine_4_input.text())
            new_cash_balance = int(self.new_cash_balance_input.text())

            # Update the UI with the new initial values
            self.previous_labels[0].setText(str(new_slot_machine_1))
            self.previous_labels[1].setText(str(new_slot_machine_2))
            self.previous_labels[2].setText(str(new_slot_machine_3))
            self.previous_labels[3].setText(str(new_slot_machine_4))
            self.previous_cash_balance_label.setText(str(new_cash_balance))

            QMessageBox.information(self, 'Uspeh', 'Početna stanja su uspešno ažurirana.')
            dialog.accept()
        except ValueError:
            QMessageBox.warning(self, 'Greška', 'Molimo unesite validna stanja za aparate i kasu.')

    def load_previous_record(self):
        """Učitava prethodni popis."""
        for i in range(4):
            self.previous_labels[i].setFixedWidth(170)
            self.difference_labels[i].setVisible(True)
            self.current_labels[i].setReadOnly(True)

        for label in self.group_edits:
            label.setReadOnly(True)
        self.delete_button.setVisible(True)
        self.handed_input.setReadOnly(True)
        self.change_date_button.setVisible(False)
        self.notebook_button.setVisible(False)
        self.deleted_censuses_button.setVisible(True)

        self.on_enter(self.total_slot_machines_difference_label, self.animation_slot_machine)
        self.on_enter(self.total_profit_loss_label, self.animation_profit_loss)

        QTimer.singleShot(320, lambda: self.total_slot_machines_difference_label.setFixedWidth(260))
        QTimer.singleShot(320, lambda: self.total_profit_loss_label.setFixedWidth(260))

        for i, previous_layout in enumerate(self.previous_layouts):
            # Remove any existing spacers at the end
            item_count = previous_layout.count()
            if item_count > 2:  # Assuming there's a spacer at index 2
                item = previous_layout.takeAt(2)
                if item.spacerItem():
                    previous_layout.removeItem(item)

            # Make the difference label visible
            self.difference_labels[i].setVisible(True)

            # Add a spacer to ensure distance between previous_edit and difference_label
            spacer_between = QSpacerItem(0, 20, QSizePolicy.Fixed, QSizePolicy.Minimum)
            previous_layout.addItem(spacer_between)

            # Add the difference label to the layout
            previous_layout.addWidget(self.difference_labels[i])
            self.previous_labels[i].setFixedWidth(170)

        if self.is_reviewing_history:
            if self.current_record_index + 1 < len(self.records):
                self.current_record_index += 1
                self.current_record = self.records[self.current_record_index]  # Set current_record
                self.populate_record(self.current_record)
                self.prosli = self.current_record


            else:
                QMessageBox.warning(self, 'Greška', 'Nema više prethodnih popisa.')
        else:
            records = session.query(slotMachineState).order_by(slotMachineState.datum.desc()).all()

            if not records:
                QMessageBox.warning(self, 'Greška', 'Nema prethodnih popisa.')
                return
            #popis
            self.records = records
            self.is_reviewing_history = True
            if str(self.records[self.current_record_index].message_list) != "":
                self.book_button.setIcon(QIcon(resource_path('book_red.png')))
            self.save_button_reconnect()

            self.current_record_index = 0  # Start from the most recent record
            self.current_record = self.records[self.current_record_index]  # Set current_record
            self.populate_record(self.current_record)
            self.prosli = self.current_record

    def load_next_record(self):
        """Učitava naredni popis."""
        if self.is_reviewing_history and self.current_record_index > 0:
            self.current_record_index -= 1
            self.populate_record(self.records[self.current_record_index])
            if str(self.records[self.current_record_index].message_list) != "":
                self.book_button.setIcon(QIcon(resource_path('book_red.png')))
        else:
            QMessageBox.warning(self, 'Greška', 'Nema više narednih popisa.')

    def delete_current_record(self):
        if not self.current_record:
            QMessageBox.warning(self, 'Greška', 'Nema popisa za brisanje.')
            return

        reply = QMessageBox.question(self, 'Potvrda brisanja',
                                     'Da li ste sigurni da želite da obrišete ovaj popis?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            try:
                # Sačuvaj podatke u bazu obrisanih popisa
                deleted_census = DeletedCensus(
                    datum=self.prosli.datum,
                    smena=self.prosli.smena,
                    vreme_brisanja=datetime.now(),
                    slot_machine_1=self.prosli.slot_machine_1,
                    slot_machine_2=self.prosli.slot_machine_2,
                    slot_machine_3=self.prosli.slot_machine_3,
                    slot_machine_4=self.prosli.slot_machine_4,
                    cash_balance=self.prosli.cash_balance,
                    group_ticket=self.prosli.group_ticket,
                    group_bingo=self.prosli.group_bingo,
                    group_live=self.prosli.group_live,
                    total_profit_loss=self.prosli.total_profit_loss,
                    total_slot_machines_difference=self.prosli.total_slot_machines_difference,
                    previous_slot_machine_1=self.prosli.previous_slot_machine_1,
                    previous_slot_machine_2=self.prosli.previous_slot_machine_2,
                    previous_slot_machine_3=self.prosli.previous_slot_machine_3,
                    previous_slot_machine_4=self.prosli.previous_slot_machine_4,
                    previous_cash_balance=self.prosli.previous_cash_balance,
                    previous_difference_1=self.prosli.previous_difference_1,
                    previous_difference_2=self.prosli.previous_difference_2,
                    previous_difference_3=self.prosli.previous_difference_3,
                    previous_difference_4=self.prosli.previous_difference_4,
                    message_list=self.prosli.message_list
                )
                deleted_session.add(deleted_census)
                deleted_session.commit()

                # Obriši popis iz originalne baze
                session.delete(self.current_record)
                session.commit()

                QMessageBox.information(self, 'Uspeh', 'Popis je uspešno obrisan.')
                self.load_previous_record()
            except Exception as e:
                QMessageBox.critical(self, 'Greška', f'Došlo je do greške pri brisanju popisa: {str(e)}')

    def prikazi_obrisane_popise(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Izbrisani popisi")
        dialog.setFixedSize(426, 380)
        dialog.setStyleSheet("background-color:#f0f0f0")
        dialog.setWindowFlags(dialog.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        # Create QListWidget for deleted censuses
        list_widget = QListWidget(dialog)
        list_widget.setStyleSheet("""
            QListWidget {
                background-color: #f0f0f0;
                color: green;
                border: none;
                font-family: Montserrat Black;
                font-size: 12px;
                box-shadow: 15px 20px 5px rgba(0, 0, 0, 0.3);  /* Shadow effect */

            }
            QListWidget::item {
                background-color: white;
                border: 1px solid #ccc;
                padding: 10px;
                margin-bottom: 5px;
                border-radius: 10px;
                box-shadow: 3px 3px 5px rgba(0, 0, 0, 0.3);  /* Shadow effect */
            }
            QListWidget::item:hover {
                background-color: #e0ffe0;
            }
            QListWidget::item:selected {
                background-color: #e0ffe0;
                color: green;
                border: 2px solid #ccc;

            }
            QListWidget::item:focus {
                outline: none;  /* Remove focus outline */
            }
            QListWidget:focus {
                outline: none;  /* Remove the focus outline from the whole widget */
            }
        """)

        list_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # Fetch deleted censuses from the database
        obrisani_popisi = deleted_session.query(DeletedCensus).all()

        # Add each deleted census as an item in the QListWidget
        for popis in obrisani_popisi:
            x = popis.datum.strftime("%d-%m-%Y")
            y = popis.vreme_brisanja.strftime("%d-%m-%Y u %H:%M")
            item_text = f"{x} - {popis.smena} | izbrisan: {y}"
            list_item = QListWidgetItem(item_text)
            list_item.setTextAlignment((Qt.AlignHCenter | Qt.AlignVCenter))

            # Attach the DeletedCensus object to the list item
            list_item.setData(Qt.UserRole, popis)

            list_widget.addItem(list_item)

        # Connect the selection signal to a function that will handle restoring the selected census
        list_widget.itemClicked.connect(self.on_census_selected)

        # Create a layout and add the list_widget to it
        dialog_layout = QVBoxLayout(dialog)
        dialog_layout.addWidget(list_widget)

        dialog.exec_()

    # Function to check existing columns and add missing ones
    def ensure_columns_exist(self):
        inspector = inspect(engine)
        columns_in_table = {col['name'] for col in inspector.get_columns('deleted_census')}
        required_columns = {
            "slot_machine_1", "slot_machine_2", "slot_machine_3", "slot_machine_4", "cash_balance",
            "group_ticket", "group_bingo", "group_live", "total_profit_loss",
            "total_slot_machines_difference", "previous_slot_machine_1", "previous_slot_machine_2",
            "previous_slot_machine_3", "previous_slot_machine_4", "previous_cash_balance",
            "previous_difference_1", "previous_difference_2", "previous_difference_3",
            "previous_difference_4", "monthly_slot_machine_1", "monthly_slot_machine_2",
            "monthly_slot_machine_3", "monthly_slot_machine_4", "message_list"
        }

        # Determine which columns are missing
        missing_columns = required_columns - columns_in_table
        if not missing_columns:
            print("No columns missing.")
            return

        # Add each missing column
        for column in missing_columns:
            column_type = "INTEGER" if "message_list" not in column else "TEXT"
            default_value = "0" if column_type == "INTEGER" else "''"
            alter_command = text(
                f"ALTER TABLE deleted_census ADD COLUMN {column} {column_type} DEFAULT {default_value};")
            try:
                session.execute(alter_command)
                print(f"Added missing column: {column}")
            except Exception as e:
                print(f"Error adding column {column}: {e}")

        session.commit()
        print("Schema updated successfully with missing columns.")

    def restore_census(self, deleted_census_instance):
        # Create a new instance of the slotMachineState class with data from the deleted census
        new_census = slotMachineState()  # Replace DeletedCensus with slotMachineState

        # Transfer all fields from the deleted instance to the new instance
        for key, value in deleted_census_instance.__dict__.items():
            if key != '_sa_instance_state' and key != 'id':  # Skip internal state and id
                setattr(new_census, key, value)

        new_census.id = None  # Ensure the ID is not reused, allowing auto-increment

        try:
            session.add(new_census)  # Add the new record to slot_machine_state table
            session.commit()
            print(f"Inserted new record into slot_machine_state with new ID.")
        except Exception as e:
            print(f"Error inserting record into slot_machine_state: {e}")
            session.rollback()

    def on_census_selected(self, item):
        """Handle the selection of a deleted census."""
        try:
            # Retrieve the DeletedCensus object from the QListWidgetItem
            selected_census = item.data(Qt.UserRole)

            if selected_census:
                print("Selected census exists")
                print(f"Selected census data: {selected_census.__dict__}")
                self.populate_restored_record(selected_census)

                try:
                    # Prompt the user for restoration
                    restore = QMessageBox.question(
                        self, "Vraćanje popisa",
                        "Želite li da vratite ovaj popis?",
                        QMessageBox.Yes | QMessageBox.No
                    )

                    if restore == QMessageBox.Yes:
                        print("Restoring the census")

                        # Expunge the object from the deleted session and make it transient
                        if deleted_session.object_session(selected_census):
                            deleted_session.expunge(selected_census)
                            make_transient(selected_census)

                        # Use the updated restore_census function to reinsert it into the main database
                        self.restore_census(selected_census)

                        # After restoring the census, delete it from the deleted_censuses table
                        deleted_session.query(DeletedCensus).filter(
                            DeletedCensus.id == selected_census.id
                        ).delete()
                        deleted_session.commit()

                        list_widget = item.listWidget()  # Assuming you are using QListWidget
                        item_index = list_widget.row(item)
                        list_widget.takeItem(item_index)  # This removes the item from the list

                        QMessageBox.information(self, "Uspeh", "Popis je uspešno vraćen.")
                        print(f"Deleted census {selected_census} from deleted_session")
                    else:
                        print("Census not restored.")
                        try:
                            self.populate_record(self.records[self.current_record_index])
                        except Exception:
                            self.reset_state()

                except Exception as e:
                    print(f"Error in restoring the census: {e}")

        except Exception as e:
            print(f"Error during selection handling: {e}")
    def reset_state(self):
        for label in self.previous_labels:
            label.setText('0')
        self.previous_cash_balance_label.setText('0')
        for label in self.current_labels:
            label.setText("")
        for label in self.group_edits:
            label.setText("")
        self.total_profit_loss_label.setText("")
        self.total_slot_machines_difference_label.setText("")
        self.handed_input.setText("")
        self.current_cash_balance_edit.setText("")
        self.new_note.setText("")
        self.book_button.setIcon(QIcon(resource_path('book.png')))

        for label in self.difference_labels:
            label.setText("")

    def populate_restored_record(self, restored_census):
        """Populates the UI with a single restored census."""
        try:
            # Inspect to check if the object is already persistent
            state = inspect(restored_census).persistent
            print(f"Object state is persistent: {state}")

            if not state:
                print("Object is not persistent, ensuring proper session handling.")
                # Expunge all to clear the session and avoid conflicts
                session.expunge_all()

                # Try adding to the session explicitly
                try:
                    session.add(restored_census)
                    session.commit()
                    print("Object added to session successfully.")
                except Exception as e:
                    print(f"Error adding object to session: {e}")
                    session.rollback()

            # Refresh the object to ensure it's synchronized with the database
            session.refresh(restored_census)
            print(f"Record data after refresh: {restored_census.__dict__}")

        except Exception as e:
            print(f"Error accessing or managing record: {e}")

        # Populate UI fields only if the object is valid and accessible
        if restored_census:
            try:
                # Populate current labels
                if len(self.current_labels) >= 4:
                    self.current_labels[0].setText(str(restored_census.slot_machine_1))
                    self.current_labels[1].setText(str(restored_census.slot_machine_2))
                    self.current_labels[2].setText(str(restored_census.slot_machine_3))
                    self.current_labels[3].setText(str(restored_census.slot_machine_4))
                else:
                    print("Error: current_labels list is too small.")

                # Populate previous labels
                if len(self.previous_labels) >= 4:
                    self.previous_labels[0].setText(str(restored_census.previous_slot_machine_1))
                    self.previous_labels[1].setText(str(restored_census.previous_slot_machine_2))
                    self.previous_labels[2].setText(str(restored_census.previous_slot_machine_3))
                    self.previous_labels[3].setText(str(restored_census.previous_slot_machine_4))
                else:
                    print("Error: previous_labels list is too small.")

                # Populate other fields
                if self.current_cash_balance_edit:
                    self.current_cash_balance_edit.setText(str(restored_census.cash_balance))
                else:
                    print("Error: current_cash_balance_edit is missing.")

                if self.previous_cash_balance_label:
                    self.previous_cash_balance_label.setText(str(restored_census.previous_cash_balance))
                else:
                    print("Error: previous_cash_balance_label is missing.")

                if len(self.group_edits) >= 3:
                    self.group_edits[0].setText(str(restored_census.group_ticket))
                    self.group_edits[1].setText(str(restored_census.group_bingo))
                    self.group_edits[2].setText(str(restored_census.group_live))
                else:
                    print("Error: group_edits list is too small.")

                if len(self.difference_labels) >= 4:
                    self.difference_labels[0].setText(str(restored_census.previous_difference_1))
                    self.difference_labels[1].setText(str(restored_census.previous_difference_2))
                    self.difference_labels[2].setText(str(restored_census.previous_difference_3))
                    self.difference_labels[3].setText(str(restored_census.previous_difference_4))
                else:
                    print("Error: difference_labels list is too small.")

                if self.date_label:
                    self.date_label.setText(f'{restored_census.datum.strftime("%d-%m-%Y")} - {restored_census.smena}')
                else:
                    print("Error: datum_label is missing.")

                if self.total_profit_loss_label:
                    self.total_profit_loss_label.setText(
                        f'Ukupan profit / gubitak: {restored_census.total_profit_loss}')
                else:
                    print("Error: total_profit_loss_label is missing.")

                if self.total_slot_machines_difference_label:
                    self.total_slot_machines_difference_label.setText(
                        f'Ukupna razlika aparata: {restored_census.total_slot_machines_difference}')
                else:
                    print("Error: total_slot_machines_differenceFR_label is missing.")

            except Exception as e:
                print(f"Error populating UI: {e}")
        else:
            print("No restored record to populate.")


class MoneyCountingDialog(QDialog):
    def __init__(self, parent, current_cash_balance_edit):
        super().__init__(parent)
        self.parent = parent
        self.trenutna_cash_balance = current_cash_balance_edit
        self.setWindowTitle("Unesite broj novčanica")
        self.setWindowIcon(QIcon(resource_path('logo.png')))
        self.setFixedSize(600, 300)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        # Apply modern stylesheet for sleek UI
        self.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #333;
            }
            QLineEdit {
                border: 1px solid #ccc;
                padding: 5px;
                border-radius: 5px;
                background-color: #f9f9f9;
            }
            QLineEdit:hover {
                border: 2px solid #4CAF50;  /* Green border on hover */
            }
            QLineEdit:focus {
                border: 2px solid #ccc;  /* Green border on focus */
                background-color: #e0ffe0;  /* Slightly different background color when focused */
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border-radius: 10px;
                padding: 10px;
                border: none;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #2e7d32;
            }
        """)
        try:
            # Creating labels and input fields
            self.labels = [
                QLabel("5000"), QLabel("2000"), QLabel("1000"), QLabel("500"),
                QLabel("200"), QLabel("100"), QLabel("50"),
                QLabel("20"), QLabel("10"), QLabel("EUR"),
                QLabel("DRUGO"), QLabel("BILLS")
            ]
            for label in self.labels:
                label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                label.setStyleSheet("""
                QLabel {
                    background-color: #fff1b8;
                    color: #7a6202;
                    border: 1px solid #ccc;
                    font-family: Montserrat;
                    font-weight: bold;
                    padding: 5px;
                    border-radius: 7px;
                }
                QLabel:hover {
                    background-color: #fff5cc;  /* Lighter green on hover */
                }
            """)

            self.inputs = [CustomLineEdit() for _ in self.labels]
        except Exception as e:
            print(e)

        # Set placeholder text to guide user input
        for i, input_field in enumerate(self.inputs):
            input_field.setPlaceholderText(f"Unesite količinu za {self.labels[i].text().replace(':', '')}")
            input_field.setStyleSheet("font-family: Montserrat; font-weight: bold;")

        # Grid layout for a more horizontal arrangement
        self.grid_layout = QGridLayout()

        for i in range(8):  # Arrange notes in two rows
            self.grid_layout.addWidget(self.labels[i], i // 4, (i % 4) * 2)
            self.grid_layout.addWidget(self.inputs[i], i // 4, (i % 4) * 2 + 1)

        for i in range(8, len(self.labels)):  # Arrange additional fields in one row
            self.grid_layout.addWidget(self.labels[i], 2, (i - 8) * 2)
            self.grid_layout.addWidget(self.inputs[i], 2, (i - 8) * 2 + 1)

        # Modernized Calculate and Cancel buttons
        self.calculate_button = QPushButton("IZRAČUNAJ")
        self.calculate_button.setStyleSheet('font-family: Montserrat Black; font-style: italic;')
        self.calculate_button.clicked.connect(self.calculate_total)

        self.cancel_button = QPushButton("ODUSTANI")
        self.cancel_button.setStyleSheet('font-family: Montserrat Black; font-style: italic;')
        self.cancel_button.clicked.connect(self.close)

        # Horizontal layout for buttons with modern styling
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.calculate_button)
        button_layout.addWidget(self.cancel_button)

        # Vertical layout to combine the grid and buttons
        main_layout = QVBoxLayout()
        main_layout.addLayout(self.grid_layout)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

    def calculate_total(self):
        try:
            # Vrednosti denominacija u dinarima
            denominations = [5000, 2000, 1000, 500, 200, 100, 50, 20, 10]  # Ima 8 elemenata
            total_amount = 0

            # Sabiranje vrednosti dinarskih novčanica
            for i in range(9):  # Sigurno prolazimo kroz 8 denominacija
                num_bills = int(self.inputs[i].text())  # Uneseni broj novčanica
                total_amount += num_bills * denominations[i]  # Sabiranje prema denominaciji

            # Pretvaranje EUR-a u dinare (multiplikacija sa 116.5)
            eur_amount = float(self.inputs[9].text())  # EUR unos
            total_amount += eur_amount * 116.5

            # Dodavanje vrednosti iz polja 'Bills' i 'Other' bez množenja
            bills_amount = int(self.inputs[10].text())  # Bills unos
            other_amount = int(self.inputs[11].text())  # Other unos
            total_amount += bills_amount + other_amount
            razlika = total_amount - int(self.trenutna_cash_balance.text())

            # Prikaz ukupne vrednosti
            QMessageBox.information(self, "Total Amount",
                                    f"Ukupno stanje u kasi: {int(total_amount)} RSD\nRazlika: {int(razlika)} RSD")

        except ValueError:
            QMessageBox.warning(self, "Greška", "Molimo unesite validne brojeve.")


if __name__ == '__main__':
    try:
        app = QApplication(sys.argv)

        # Forsiraj upotrebu Qt stila (Fusion)
        app.setStyle("Fusion")

        tracker = BettingShiftTracker()
        sys.exit(app.exec_())
    except EnvironmentError as e:
        print(e)
