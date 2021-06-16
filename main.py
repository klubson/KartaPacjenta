import fhirpy as fhir
from fhirpy import SyncFHIRClient
from streamlit.components.v1 import html as st_html
import streamlit as st
import multipage_framework.multipage as mult
import datetime

HAPI_BASE_URL = "http://hapi.fhir.org/baseR4"
#HAPI_BASE_URL = "https://server.fire.ly/r4"
#HAPI_BASE_URL = "http://test.fhir.org/r4"


def main_page(prev_vars):
    st.title("main page")
    client = SyncFHIRClient(
        HAPI_BASE_URL
    )
    patients = client.resources('Patient')
    if prev_vars is not None:
        user_input = prev_vars
    else:
        user_input = ""
    user_input = st.text_input("Name", user_input)
    mult.save([user_input], name='search', page_names=["main page"])
    if user_input != "":
        patients = patients.search(family__contains=user_input).sort('name')
    else:
        patients = patients.sort('name')
    results = patients.limit(100).fetch()
    len = patients.count()
    st.write("Results: " + str(len))
    if len > 100:
        st.write("first 100")
    st.markdown("---")
    for patient in results:
        dic = patient.serialize()
        name_s = ""
        if 'given' in dic['name'][0]:
            for name in dic['name'][0]['given']:
                name_s += name + " "
        if 'family' in dic['name'][0]:
            name_s += dic['name'][0]['family']
        st.write(name_s)
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
        if 'telecom' in pat:
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
        start_date = left.date_input(min_value=datetime.datetime(year=1900, month=1, day=1), label='start')
        end_date = right.date_input(min_value=datetime.datetime(year=1900, month=1, day=1), label='end')
        obs = observations.fetch()
        obs.sort(key=sorter, reverse=True)
        for el in obs:
            if end_date >= conv(el['effectiveDateTime']).date() >= start_date:
                st.markdown(f"## Observation *{el['effectiveDateTime']}*")
                st.write(el['id'])
                codings = []
                for it in el:
                    item = el[it]
                    if it == 'valueQuantity':
                        codings.append(f"{item['value']} {item['unit']}")
                    elif isinstance(item, dict):
                        if 'coding' in item:
                            if 'display' in item['coding'][0]:
                                codings.append(item['coding'][0]['display'])
                    elif isinstance(item, list):
                        for i in item:
                            if isinstance(i, dict):
                                if 'coding' in i:
                                    codings.append(i['coding'][0]['display'])
                cols = st.beta_columns(len(codings))
                for i in range(len(codings)):
                    cols[i].markdown(f"**{codings[i]}**")

                obs_ref = client.reference('Observation', el['id'])

                if 'encounter' in el:
                    requests = client.resources('MedicationRequest')
                    requests = requests.search(encounter=el['encounter']['reference'])
                    requests = requests.search()
                    requests = requests.fetch()
                    if len(requests) > 0:
                        st.markdown('### Medication Requests')
                        for med in requests:
                            if 'medicationReference' in med:
                                st.write(med['medicationReference']['display'])
                            elif 'medicationCodeableConcept' in med:
                                for co in med['medicationCodeableConcept']['coding']:
                                    st.write(co['display'])
                statements = client.resources('MedicationStatement')
                statements = statements.search(part_of=obs_ref)
                statements = statements.fetch()
                if len(statements) > 0:
                    st.markdown("### Medication Statements")
                    for med in statements:
                        if 'medicationReference' in med:
                            st.write(med['medicationReference']['display'])
                        elif 'medicationCodeableConcept' in med:
                            for co in med['medicationCodeableConcept']['coding']:
                                st.write(co['display'])
                st.markdown("---")

    else:
        st.write("No patient selected")


if __name__ == "__main__":
    mult.start_app()
    app = mult.MultiPage()
    app.disable_navbar()
    app.add_app("main page", main_page)
    app.add_app("patient", patient_page)
    app.run()
