import fhirpy as fhir
from fhirpy import SyncFHIRClient
from streamlit.components.v1 import html as st_html
import streamlit as st
import multipage_framework.multipage as mult

HAPI_BASE_URL = "http://hapi.fhir.org/baseR4"


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
                mult.save(var_list=[int(dic['id'])], name="patient_id", page_names=["patient"])
                mult.change_page(mult.read_page()+1)
            st.markdown("---")


def patient_page(prev_vars):
    st.title("patient")
    st.write(prev_vars)
    if st.button("go to main page"):
        mult.change_page(mult.read_page()-1)


if __name__ == "__main__":
    mult.start_app()
    app = mult.MultiPage()
    app.disable_navbar()
    app.add_app("main page", main_page)
    app.add_app("patient", patient_page)
    app.run()
