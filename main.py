import io
from os import getenv

import pandas as pd
import streamlit as st

st.set_page_config(
    layout="wide",
    menu_items={
        "Get help": None,
        "Report a Bug": None,
        "About": None,
    },
)

st.title("Mapa de talento AYI")

col1, _ = st.columns([1, 3])

with col1:
    email = st.text_input(
        "INGRESE SU USUARIO", placeholder="USUARIO", label_visibility="hidden"
    )

    pwd = st.text_input(
        "INGRESE SU CONTRASEÑA",
        placeholder="CONSTRASEÑA",
        label_visibility="hidden",
        type="password",
    )

if email == "" or pwd == "":

    st.info("INGRESE SUS CREDENCIALES")

elif email == getenv('USER') and pwd == getenv('PASSWORD'):

    filters = dict()

    data_bytes = io.BytesIO()

    googleSheetId = getenv('SHEET_ID')
    worksheetName = getenv('SHEET_NAME')

    SHEET_URL = "https://docs.google.com/spreadsheets/d/{0}/gviz/tq?tqx=out:csv&sheet={1}".format(
        googleSheetId, worksheetName
    )

    data = pd.read_csv(SHEET_URL, header=0)

    data.columns = [x.replace(" ", "_") for x in data.columns]

    data.columns = [x.replace("__", "_") for x in data.columns]

    data.columns = [x.replace("[", "") for x in data.columns]

    data.columns = [x.replace("]", "") for x in data.columns]

    data.columns = [x.replace("¿", "") for x in data.columns]

    data.columns = [x.replace("?", "") for x in data.columns]

    data.columns = [x.replace("(", "") for x in data.columns]

    data.columns = [x.replace(")", "") for x in data.columns]

    data.columns = [x.replace(":", "") for x in data.columns]

    data.columns = [x.replace("-", "") for x in data.columns]

    data.columns = [x.replace("!", "") for x in data.columns]

    data.columns = [x.replace("¡", "") for x in data.columns]

    data.columns = [x[0:-1] if x.endswith("_") else x for x in data.columns]

    data.columns = [x.replace("/", "_o_") for x in data.columns]

    data.fillna("N/A", inplace=True)

    t1, t2, t3 = st.tabs(
        [
            "Filtrar por correo/nombre",
            "Filtrar por conocimiento",
            "Filtrar por apellido",
        ]
    )

    with t1:

        st.subheader("Ejemplos de búsqueda:")
        st.markdown(
            """
            - CARLOS MENDEZ
            - Carlos Mendez
            - Carlos mendez
            - carlos mendez
            - carlos.mendez
            - carlos.mendez@ayi.group
                    """
        )

        l_col, _ = st.columns([2, 4])

        with l_col:
            search = st.text_input("Buscar:")
            search_button = st.button("Buscar")

        if search or search_button:

            email = search.lower()

            if " " in email:
                email = email.replace(" ", ".")

            if not "@" in email:

                email = f"{email}@ayi.group"

            mask = data["Dirección_de_correo_electrónico"] == email

            user = data[mask]

            st.title("Resultado:")

            for i, x in enumerate(user.columns):
                if not i == 0:
                    if not user.iloc[0, i] == "N/A":
                        if x == "Dirección_de_correo_electrónico":
                            st.markdown("# {}".format(user[x].values.any()))
                            continue
                        st.markdown(
                            """### {}:
                                {}""".format(
                                x, user[x].values.any()
                            )
                        )
        else:
            display_data = data
            display_data.columns = [x for x in display_data.columns]
            st.dataframe(display_data)

    with t2:

        cols = (
            x
            for x in data.columns
            if not "correo" in x.lower()
            and not "conocimiento" in x.lower()
            and not "caso" in x.lower()
            and not ".1" in x.lower()
            and not "marca_temporal" in x.lower()
        )

        columns = st.multiselect("Columnas:", [x for x in cols], key="exc")

        query_mode = " | "

        exclusive = st.checkbox("Condiciones excluyentes")

        if exclusive:
            query_mode = " & "

        if columns:

            for x in data.columns:
                if x in columns:
                    label = x
                    filters[label] = st.selectbox(
                        label,
                        (
                            value
                            for value in data[x].unique()
                            if ".1" not in str(value) and not value == "N/A"
                        ),
                    )

            query = query_mode.join(
                [
                    "{}.str.contains('{}')".format(key, value)
                    for key, value in filters.items()
                ]
            )

            filtered_data = data.query(query)

            st.write(filtered_data)

            filtered_data.to_excel(data_bytes)

        else:
            display_data = data

            st.dataframe(display_data)

            data.to_excel(data_bytes)

        col1, _, _ = st.columns([1, 1, 3])

    with col1:

        file_name = st.text_input(
            "Nombre del archivo (enter para aplicar):", placeholder="Data"
        )

        if file_name == "":
            file_name = "Data"

        file_format = st.selectbox("Formato:", [".xlsx (Excel)", ".csv"])

        if " " in file_format:
            file_format = file_format.split(" ")[0]

        st.download_button(
            "Descargar {}".format(file_format),
            data_bytes.getvalue(),
            "{}{}".format(file_name, file_format),
            "text/excel",
        )

else:
    st.error("ACCESO INCORRECTO")
