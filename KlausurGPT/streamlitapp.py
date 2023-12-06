import streamlit as st
from generatorapp import your_openai_function
from generatorapp import feedback_openai_function
from generatorapp import generate_pdf_from_responses
import requests


st.title('KlausurGPT')


if 'page' not in st.session_state:
    st.session_state['page'] = 'main_page'
if 'Wissensfragen' not in st.session_state:
    st.session_state['Wissensfragen'] = False
if 'Objektorientierte Programmierung' not in st.session_state:
    st.session_state['Objektorientierte Programmierung'] = False
if 'Verkettete Listen' not in st.session_state:
    st.session_state['Verkettete Listen'] = False
if 'Bäume' not in st.session_state:
    st.session_state['Bäume'] = False
if 'Fehleranalyse' not in st.session_state:
    st.session_state['Fehleranalyse'] = False
if 'sub_values' not in st.session_state:
    st.session_state['sub_values'] = {}

if st.session_state['page'] == 'main_page':
    st.title("Willkommen")
    st.text("Bitte wählen Sie die gewünschten Aufgabentypen")
    st.session_state['generated_strings'] = [] 
    st.session_state['responses'] = []

    st.session_state['Wissensfragen'] = st.checkbox('Wissensfragen', st.session_state['Wissensfragen'])
    st.session_state['Objektorientierte Programmierung'] = st.checkbox('Objektorientierte Programmierung', st.session_state['Objektorientierte Programmierung'])
    st.session_state['Verkettete Listen'] = st.checkbox('Verkettete Listen', st.session_state['Verkettete Listen'])
    st.session_state['Bäume'] = st.checkbox('Bäume', st.session_state['Bäume'])
    st.session_state['Fehleranalyse'] = st.checkbox('Fehleranalyse', st.session_state['Fehleranalyse'])

    if st.button("Weiter"):
        st.session_state['page'] = 'sub_page'
        st.experimental_rerun() 

elif st.session_state['page'] == 'sub_page':
    st.title("Spezifikation")

    sub_options = {
        'Wissensfragen': ["Allgemeine Fragen", "Ausgabe einer Schleife", "Variablen Initialisierung", "Code Ausgabe", "Code Bedeutung", "Vorteil Nachteil"],
        'Objektorientierte Programmierung': ["Konstruktor", "Vererbung", "Polymorphie", "Objekte erzeugen", "Interface", "Arrays", "Listen", "Komplexe Methoden", "Funktionalität der Methoden ausführlich Beschreiben", "Kreative Aufgabenstruktur", "Definierte Vorgabe von Klassen, Eigenschaften Methoden"],
        'Verkettete Listen': ["Einfach verkettet", "Doppelt verkettet", "Hinzufügen am Anfang", "Leere Liste", "Enthält ein Element", "Entfernt ein Element", "Zählt Element", "Umkehren der Liste", "Gibt einen Wert zu einem Index zurück"],
        'Bäume': ["Definition der Datenstruktur", "Anzahl Knoten", "Pre-In-Post-Order", "Ausgabe der Knoten", "Summe aller Knoten", "Einfügen eines Knoten", "Suchen eines Knoten", "Löschen eines Knoten", "Kleinster Knoten", "Größter Knoten"],
        'Fehleranalyse': ["Objekte prüfen", "Methoden Ausgaben benennen"]
    }

    checkbox_labels = ['Wissensfragen', 'Objektorientierte Programmierung', 'Verkettete Listen', 'Bäume', 'Fehleranalyse']

    for label in checkbox_labels:
        if st.session_state[label]:
            if label not in st.session_state['sub_values']:
                st.session_state['sub_values'][label] = []
            st.session_state['sub_values'][label] = st.multiselect(f'Wählen Sie Werte für {label}:', sub_options[label], st.session_state['sub_values'][label])

    predefined_strings = {
        'Wissensfragen': 'Denke dir eine neue Fragen nachdem Aufgabentyp Wissenfragen aus. ',
        'Objektorientierte Programmierung': 'Denke dir eine neue Aufgabe nachdem Aufgabentyp ObjektorientierteProgrammierung aus. ',
        'Verkettete Listen': 'Denke dir eine neue Aufgabe nachdem Aufgabentyp VerketteListen aus.  ',
        'Bäume': 'Denke dir eine neue Übungsaufgabe nachdem Aufgabetyp Bäume aus. ',
        'Fehleranalyse': 'Denke dir eine neue Aufgabe nachdem Aufgabentyp Fehleranalyse aus. '
    }

    if 'chat_history' not in st.session_state:
        st.session_state['chat_history'] = []

    if st.button("Generierung starten"):
        combined_strings = []

        for checkbox, selected_values in st.session_state['sub_values'].items():
            if st.session_state[checkbox]:
                combined_string = predefined_strings[checkbox]

                for value in selected_values:
                    spec_string = f"Befolge diese Spezifikation ### {value} ###"
                    combined_string += spec_string
                
                combined_strings.append(combined_string)

        # Kombinierter String für alle Checkboxen
        final_string = "; ".join(combined_strings)
        st.write(f"Kombinierter String: {final_string}")
        with st.spinner('Bitte warten, Ihre Aufgaben werden generiert...'):
            for strg in combined_strings:
                response = your_openai_function(strg)  
                st.session_state['chat_history'].append((strg, response))
                st.session_state['responses'].append(response) 
        st.session_state['page'] = 'response_page'

        print("Kombinierter String für das Backend:", final_string)
        st.experimental_rerun()
    
elif st.session_state['page'] == 'response_page':
    st.title("Generierte Aufgaben")
    for i, response in enumerate(st.session_state['responses']):
        st.write(f"Antwort {i+1}: {response}")
    if st.button("PDF erstellen"):
        generate_pdf_from_responses(st.session_state['responses'])
        st.write("PDF wurde erstellt.")

    if st.button("Zurück zur Hauptseite"):
        st.session_state['page'] = 'main_page'

