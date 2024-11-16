import streamlit as st
from streamlit_option_menu import option_menu
import extra_streamlit_components as stx
import psycopg2
import pandas as pd

st.set_page_config(layout="wide")

dsn = "postgresql://eh5b17:xau_h6oA2zsTsNzOhau4F6OIMc1zm5iIbRsT1@us-east-1.sql.xata.sh/hackathon:main?sslmode=require"

def obtener_proveedores():
    conn = psycopg2.connect(dsn)
    cursor = conn.cursor()
    query = "SELECT razon FROM estadisticas_contratos;"
    cursor.execute(query)
    resultados = [fila[0].upper() for fila in cursor.fetchall()]
    cursor.close()
    conn.close()
    return resultados

def consultar_proveedor(razon):
    conn = psycopg2.connect(dsn)
    cursor = conn.cursor()
    query = f"SELECT * FROM supersociedades where razon = '{razon.lower()}';"
    cursor.execute(query)
    infoProveedor = cursor.fetchall()
    cursor.close()
    conn.close()
    return infoProveedor

def consultar_experiencia(razon):
    conn = psycopg2.connect(dsn)
    cursor = conn.cursor()
    query = f"SELECT * FROM estadisticas_contratos where razon = '{razon.lower()}';"
    cursor.execute(query)
    infoProveedor = cursor.fetchall()
    cursor.close()
    conn.close()
    return infoProveedor

if "proveedores" not in st.session_state:
    st.session_state.proveedores = obtener_proveedores()

proveedores = st.session_state.proveedores

iconos = ["house"] + ["building"] * (len(proveedores) - 1)

with st.sidebar:
    selected = option_menu(
        "Proveedores en construcción", 
        ["Menú"] + proveedores,
        icons=iconos,
        menu_icon="tools",
        default_index=0,
        key="menu_proveedores"
    )

st.session_state.selected_proveedor = selected

if selected != "Menú":

    st.session_state.info_selected_proveedor = consultar_proveedor(st.session_state.selected_proveedor)
    st.session_state.experiencia_selected_proveedor = consultar_experiencia(st.session_state.selected_proveedor)

    tabs = st.tabs(["Información general", 
                "Información financiera",
                "Información judicial",
                "Control financiero",
                "Experiencia"])
    
    # Lógica para cada pestaña
    with tabs[0]:
        st.write(f"## Información general de {selected} 🏢")

        html = """
        <div style="display: flex; justify-content: space-between; gap: 20px;">
            <div style="width: 48%; padding: 10px; border: 1px solid #ccc; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
                <h3 style="color: #1a73e8;">🆔 NIT</h3>
                <p><strong>{}</strong></p>
            </div>
            <div style="width: 48%; padding: 10px; border: 1px solid #ccc; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
                <h3 style="color: #1a73e8;">📅 Fecha de constitución</h3>
                <p><strong>{}</strong></p>
            </div>
        </div>

        <div style="display: flex; justify-content: space-between; gap: 20px; margin-top: 20px;">
            <div style="width: 48%; padding: 10px; border: 1px solid #ccc; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
                <h3 style="color: #1a73e8;">📍 Ubicación</h3>
                <p><strong>{}</strong></p>
            </div>
            <div style="width: 48%; padding: 10px; border: 1px solid #ccc; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
                <h3 style="color: #1a73e8;">🏢 Actividad económica</h3>
                <p><strong>{}</strong></p>
            </div>
        </div>

        <div style="display: flex; justify-content: space-between; gap: 20px; margin-top: 20px;">
            <div style="width: 48%; padding: 10px; border: 1px solid #ccc; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
                <h3 style="color: #1a73e8;">⚙️ Estado</h3>
                <p><strong>{}</strong></p>
            </div>
            <div style="width: 48%; padding: 10px; border: 1px solid #ccc; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
                <h3 style="color: #1a73e8;">📊 Fecha de corte</h3>
                <p><strong>{}</strong></p>
            </div>
        </div>
        """

        nit = st.session_state.info_selected_proveedor[0][0]
        nit = f"{nit[:3]}.{nit[3:6]}.{nit[6:]}"
        fecha_constitucion = st.session_state.info_selected_proveedor[0][4]
        ubicacion = st.session_state.info_selected_proveedor[0][3].upper()
        actividad_economica = st.session_state.info_selected_proveedor[0][2]
        estado = st.session_state.info_selected_proveedor[0][5].capitalize()
        fecha_corte = st.session_state.info_selected_proveedor[0][6]

        html = html.format(nit, fecha_constitucion, ubicacion, actividad_economica, estado, fecha_corte)

        st.markdown(html, unsafe_allow_html=True)

        st.markdown("---")

        st.success("Esta información está basada en los datos más recientes disponibles. ✅")

    with tabs[1]:
        st.write(f"## Información financiera de {selected} 🏢")
        st.write("*Algunos datos son respecto al corte anterior.")

        html = """
            <div style="display: flex; justify-content: space-between; gap: 20px;">
                <div
                    style="width: 48%; padding: 10px; border: 1px solid #ccc; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
                    <h3 style="color: #1a73e8;">📊 Situación Financiera</h3>
                    <p><strong>Activos:</strong> {}</p>
                    <p><strong>Pasivos:</strong> {}</p>
                    <p><strong>Patrimonio:</strong> {}</p>
                </div>
                <div
                    style="width: 48%; padding: 10px; border: 1px solid #ccc; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
                    <h3 style="color: #1a73e8;">📈 Resultado Integral</h3>
                    <p><strong>Ingreso:</strong> {}</p>
                    <p><strong>Ganancia:</strong> {}</p>
                </div>
            </div>

            <!-- Fila para Indicadores -->
            <div style="display: flex; justify-content: space-between; gap: 20px; margin-top: 20px;">
                <div
                    style="width: 48%; padding: 10px; border: 1px solid #ccc; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
                    <h3 style="color: #1a73e8;">📉 Indicadores</h3>
                    <p><strong>Prueba:</strong> {}</p>
                    <p><strong>Endeudamiento:</strong> {}</p>
                </div>
                <div
                    style="width: 48%; padding: 10px; border: 1px solid #ccc; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
                    <h3 style="color: #1a73e8;">📊 ROA y ROE</h3>
                    <p><strong>ROA:</strong> {}</p>
                    <p><strong>ROE:</strong> {}</p>
                </div>
            </div>

            <!-- Fila para Flujo de Efectivo -->
            <div style="display: flex; justify-content: space-between; gap: 20px; margin-top: 20px;">
                <div
                    style="width: 48%; padding: 10px; border: 1px solid #ccc; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
                    <h3 style="color: #1a73e8;">💸 Flujo de Efectivo</h3>
                    <p><strong>Actividades Operación:</strong> {}</p>
                    <p><strong>Actividades Inversión:</strong> {}</p>
                </div>
                <div
                    style="width: 48%; padding: 10px; border: 1px solid #ccc; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
                    <h3 style="color: #1a73e8;">💰 Actividades Financiación</h3>
                    <p><strong>Actividades Financiación:</strong> {}</p>
                </div>
            </div>

            <!-- Fila para Otro Resultado Integral -->
            <div style="display: flex; justify-content: space-between; gap: 20px; margin-top: 20px;">
                <div
                    style="width: 48%; padding: 10px; border: 1px solid #ccc; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
                    <h3 style="color: #1a73e8;">📊 Otro Resultado Integral</h3>
                    <p><strong>Ganancia Integral:</strong> {}</p>
                </div>
                <div
                    style="width: 48%; padding: 10px; border: 1px solid #ccc; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
                    <h3 style="color: #1a73e8;">📈 Resultado Integral</h3>
                    <p><strong>Resultado Integral:</strong> {}</p>
                </div>
            </div>

            <!-- Fila para Procesos en Superintendencia -->
            <div style="display: flex; justify-content: space-between; gap: 20px; margin-top: 20px;">
                <div
                    style="width: 48%; padding: 10px; border: 1px solid #ccc; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
                    <h3 style="color: #1a73e8;">⚖️ Procesos en Superintendencia</h3>
                    <p><strong>Activos en Proceso:</strong> {}</p>
                </div>
                <div
                    style="width: 48%; padding: 10px; border: 1px solid #ccc; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
                    <h3 style="color: #1a73e8;">📂 Procesos Cerrados</h3>
                    <p><strong>Procesos Cerrados:</strong> {}</p>
                </div>
            </div>
        """

        # Situación financiera
        activos = f"${int(st.session_state.info_selected_proveedor[0][7]):,} M"
        pasivos = f"${int(st.session_state.info_selected_proveedor[0][8]):,} M"
        patrimonio = f"${int(st.session_state.info_selected_proveedor[0][9]):,} M"

        # Resultado integral
        ingreso = f"${int(st.session_state.info_selected_proveedor[0][10]):,} M"
        ganancia = f"${int(st.session_state.info_selected_proveedor[0][11]):,} M"

        # Indicadores
        prueba = str(st.session_state.info_selected_proveedor[0][12]) + " Veces"
        endeudamiento = str(st.session_state.info_selected_proveedor[0][13]) + "%"
        roa = str(st.session_state.info_selected_proveedor[0][14]) + "%"
        roe = str(st.session_state.info_selected_proveedor[0][15]) + "%"

        # Flujo de efectivo
        act_operacion = f"${int(st.session_state.info_selected_proveedor[0][16]):,} M"
        act_inversion = f"${int(st.session_state.info_selected_proveedor[0][17]):,} M"
        act_financiacion = f"${int(st.session_state.info_selected_proveedor[0][18]):,} M"

        # Otro resultado integral
        integralGanancia = f"${int(st.session_state.info_selected_proveedor[0][19]):,} M"
        resultado_integral = f"${int(st.session_state.info_selected_proveedor[0][20]):,} M"

        # Procesos en superintendencia
        proActivos = str(st.session_state.info_selected_proveedor[0][21])
        proCerrados = str(st.session_state.info_selected_proveedor[0][22])

        html_formatted = html.format(activos, pasivos, patrimonio, ingreso, ganancia, prueba, endeudamiento, roa, roe, act_operacion, act_inversion, act_financiacion, integralGanancia, resultado_integral, proActivos, proCerrados)

        st.markdown(html_formatted, unsafe_allow_html=True)

        st.markdown("---")

        st.success("Esta información está basada en los datos más recientes disponibles. ✅")

    with tabs[2]:
        st.header(f"Información judicial de {selected} 🏛️")
        st.write("Se busca que esta información sea extraída de la consulta de procesos de la rama judicial.")
        
        df = pd.read_csv('consultaprocesos.csv', sep=',', quotechar='"')
        df = pd.DataFrame(df)
        st.dataframe(df)

        st.markdown("---")

        st.success("Esta información está basada en los datos más recientes disponibles. ✅")

    with tabs[3]:
        st.header(f"Control financiero de {selected} 👨‍⚖️")
        st.write("Se busca que esta información sea extraída de Empresas Col, encargada de reportar datos faltantes es supersociedades.")
        data = {
            "Pregunta": [
                "¿La Compañía Está Obligada A Tener Revisor Fiscal?",
                "¿El Revisor Fiscal Pertenece A Una Firma?",
                "¿A Qué Firma Pertenece El Revisor Fiscal?",
                "¿Los Estados Financieros Están Acompañados Del Dictamen Del Revisor Fiscal?",
                "Concepto Del Revisor Fiscal En Su Informe",
                "¿Estos Estados Financieros Presentan Información Reexpresada?",
                "¿La Información Reexpresada Corresponde A?",
                "Reexpresión Según Normatividad Que Aplique"
            ],
            "Respuesta": [
                "Sí",
                "Sí",
                "DNI SAS",
                "Sí",
                "03. LIMPIO",
                "No",
                "No aplica",
                "No aplica"
            ]
        }

        df = pd.DataFrame(data)

        st.dataframe(
            df,
        )

    with tabs[4]:
        st.header(f"Experiencia de {selected} 🏢")
        st.write("Se busca que esta información sea extraída de Empresas Col, encargada de reportar datos faltantes de supersociedades.")

        html = """
        <div style="display: flex; justify-content: center; margin-top: 20px;">
            <div style="width: 100%; padding: 20px; border: 1px solid #ccc; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
                <h3 style="color: #1a73e8; text-align: center;">🕒 Tiempo Contratando</h3>
                <p><strong>Fecha primer proceso:</strong> {}</p>
                <p><strong>Fecha último proceso:</strong> {}</p>
                <p><strong>Años contratando:</strong> {}</p>
            </div>
        </div>

        <div style="display: flex; justify-content: space-between; margin-top: 20px; gap: 20px;">
            <div style="width: 48%; padding: 20px; border: 1px solid #ccc; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
                <h3 style="color: #1a73e8; text-align: center;">⏳ Duración Promedio de los Procesos</h3>
                <p><strong>Duración promedio:</strong> {} días</p>
            </div>
            <div style="width: 48%; padding: 20px; border: 1px solid #ccc; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
                <h3 style="color: #1a73e8; text-align: center;">📑 Cantidad de Procesos Adjudicados</h3>
                <p><strong>Procesos adjudicados:</strong> {} procesos</p>
            </div>
        </div>

        <div style="display: flex; justify-content: space-between; margin-top: 20px; gap: 20px;">
            <div style="width: 48%; padding: 20px; border: 1px solid #ccc; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
                <h3 style="color: #1a73e8; text-align: center;">💰 Valor Total Adjudicado</h3>
                <p><strong>Valor total adjudicado:</strong> {} COP</p>
            </div>
            <div style="width: 48%; padding: 20px; border: 1px solid #ccc; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
                <h3 style="color: #1a73e8; text-align: center;">💰 Valor Promedio Adjudicado</h3>
                <p><strong>Valor promedio adjudicado:</strong> {} COP</p>
            </div>
        </div>
        <div style="display: flex; justify-content: center; margin-top: 20px;">
            <div style="width: 100%; padding: 20px; border: 1px solid #ccc; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
                <h3 style="color: #1a73e8; text-align: center;">🏆 Puntaje</h3>
                <p><strong>Puntaje total:</strong> 85/100</p>
                <p><em>Este puntaje actualmente es un valor estático. En el futuro, se calculará automáticamente en función de los datos disponibles.</em></p>
            </div>
        </div>
        """

        fecha_min = str(st.session_state.experiencia_selected_proveedor[0][2])
        fecha_max = str(st.session_state.experiencia_selected_proveedor[0][3])
        contratando = str(st.session_state.experiencia_selected_proveedor[0][4])
        duracion_promedio = str(st.session_state.experiencia_selected_proveedor[0][5])
        procesos_adjudicados = str(st.session_state.experiencia_selected_proveedor[0][6])
        valor_total_adjudicado = f"${int(st.session_state.experiencia_selected_proveedor[0][7]):,} M"
        valor_promedio_adjudicado = f"${int(st.session_state.experiencia_selected_proveedor[0][8]):,} M"

        html_formatted = html.format(fecha_min, fecha_max, contratando, duracion_promedio, procesos_adjudicados, valor_total_adjudicado, valor_promedio_adjudicado)

        st.markdown(html_formatted, unsafe_allow_html=True)

        st.markdown("---")

        st.success("Esta información está basada en los datos más recientes disponibles. ✅")
        
else:
    st.write(f"## Menú 🏠")
    st.markdown(f"""
    <iframe title="Analisis_Proveedores_Defi" width="100%" height="600" src="https://app.powerbi.com/view?r=eyJrIjoiNzJkZjVjYWEtYmYwOS00MjRlLTgwMzgtNzU4ZDY1OWI0ODQ0IiwidCI6IjA4YjViMTkzLWI5YmItNDNmMi05MjJiLTdlMjk0OGE0MDhlOSIsImMiOjR9" frameborder="0" allowFullScreen="true"></iframe>
    """, unsafe_allow_html=True)

    st.markdown("---")

    st.write("Selecciona un proveedor para ver su información.")

    st.markdown("---")

    st.success("Esta información está basada en los datos más recientes disponibles. ✅")