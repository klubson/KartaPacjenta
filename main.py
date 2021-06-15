import fhirpy as fhir
from fhirpy import SyncFHIRClient
from streamlit.components.v1 import html as st_html
import streamlit as st
import multipage_framework.multipage as mult
import datetime

#HAPI_BASE_URL = "http://hapi.fhir.org/baseR4"
HAPI_BASE_URL = "https://server.fire.ly/r4"
#HAPI_BASE_URL = "http://test.fhir.org/r4"

def main_page(prev_vars):
    st.title("main page")
    client = SyncFHIRClient(
        HAPI_BASE_URL
    )
    patients = client.resources('Patient')
    user_input = st.text_input("Name", "")
    if user_input != "":
        patients = patients.search(family__contains=user_input).sort('name')
        results = patients.fetch()
        st.write("Results: " + str(len(results)))
        st.markdown("---")
        for patient in results:
            dic = patient.serialize()
            name_s = ""
            if 'given' in dic['name'][0]:
                for name in dic['name'][0]['given']:
                    name_s += name + " "
            st.write(name_s + dic['name'][0]['family'])
            if st.button("Go", key=dic['id']):
                mult.save(var_list=[dic['id']], name="patient_id", page_names=["patient"])
                mult.change_page(mult.read_page()+1)
            st.markdown("---")


def conv(date):
    return datetime.datetime.fromisoformat(date)


def sorter(e):
    date = e['effectiveDateTime']
    x = conv(date).strftime("%Y/%m/%d %H:%M:%S")
    return x


def patient_page(prev_vars):
    st.title("patient")
    if st.button("go to main page"):
        mult.change_page(mult.read_page()-1)
    if prev_vars is not None:
        client = SyncFHIRClient(
            HAPI_BASE_URL
        )
        patient = client.resources('Patient')
        patient = patient.search(_id=prev_vars)
        pat = patient.first()

        pat_raw = patient.fetch_raw()
        start_date = ""
        end_date = ""

        medication_statements = client.resources('MedicationStatement')
        medication_statements = medication_statements.first()

        data_string = "## "
        if 'prefix' in pat['name'][0]:
            data_string += " ".join(pat['name'][0]['prefix']) + " "
        data_string += " ".join(pat['name'][0]['given']) + " "
        data_string += pat['name'][0]['family'] + "\n"

        for naming in pat['name']:
            if 'use' in naming:
                if naming['use'] == 'maiden':
                    data_string += f"- **Maiden name**: {naming['family']} _(till: {naming['period']['end']})_\n"

        data_string += f"- **Gender**: {pat['gender']}\n"
        for com in pat['telecom']:
            if 'value' in com:
                if com['system'] == 'phone':
                    if com['use'] != 'old':
                        data_string += f"- **{com['use'].capitalize()} phone**: {com['value']}\n"
                elif com['system'] == 'email':
                    data_string += f"- **Email:** {com['value']}\n"
        data_string += f"- **Date of birth**: {pat['birthDate']}\n"
        data_string += f"- **Id**: {pat['id']}\n"

        ref = client.reference('Patient', id=prev_vars)
        observations = client.resources('Observation')
        observations = observations.search(patient=ref)

        st.markdown(data_string)
        left, right = st.beta_columns(2)
        start_date = left.date_input('start')
        end_date = right.date_input('end')
        obs = observations.fetch()
        obs.sort(key=sorter, reverse=True)
        for el in obs:
            if end_date >= conv(el['effectiveDateTime']).date() >= start_date:
                st.write(el['effectiveDateTime'])

    else:
        st.write("No patient selected")


if __name__ == "__main__":
    mult.start_app()
    app = mult.MultiPage()
    app.disable_navbar()
    app.add_app("main page", main_page)
    app.add_app("patient", patient_page)
    app.run()
