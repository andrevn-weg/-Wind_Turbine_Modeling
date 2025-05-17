import streamlit as st
from PIL import Image
import os
import base64
import pandas as pd
from pathlib import Path

# Import CSS loader
from utils.css_loader import load_css

# Load centralized CSS
project_root = Path(__file__).parent.parent
css_path = os.path.join(project_root, "static", "css", "material_styles.css")
load_css(css_path)

# Main title
st.markdown("""
<div class="page-main-header">
    <h1>About <span style="color: rgb(219 123 52); text-shadow: 2px 2px 4px rgba(0,0,0,0.3); font-weight: bold;">GHFM Analytics</span></h1>
    <p>Guarded Hot Flow Meter Technique for Thermal Conductivity Measurement</p>
</div>
""", unsafe_allow_html=True)

# Project introduction
with st.container():
    st.markdown("""
    <div class="section-header">
        <h4>🔍 Introduction</h4>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("""
    <div class="detail-container">
    <p>This project implements the standardized test method for measuring thermal conductivity 
    in solid materials using the Guarded Hot Flow Meter (GHFM) technique, as described in 
    ASTM E1225-20 standard.</p>
    <p>The system allows for precise determination of thermal conductivity (λ) of homogeneous 
    solid materials under controlled conditions. </p>
    
    </div> 
    """, unsafe_allow_html=True)

# Terminology
with st.container():
    st.markdown("""
    <div class="section-header">
        <h4>📚 Terminology</h4>
    </div>
    """, unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    col1.markdown("""
    <div class="detail-container">
        <div class="thermal-section">
            <h4>📝 Specific Definitions</h4>
        </div>
        <ul style="list-style-type: none; padding-left: 0;">
            <li style="padding: 10px 0; border-bottom: 1px solid #eee;">
                <b>Thermal conductivity, λ:</b> Rate of heat flow, under steady-state conditions, through a unit area, per unit of temperature gradient in the direction perpendicular to the area.
            </li>
            <li style="padding: 10px 0;">
                <b>Apparent thermal conductivity:</b> When other modes of heat transfer (besides conduction) are present, the results obtained by this method represent the apparent (or effective) thermal conductivity of the tested material.
            </li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    col2.markdown("""
    <div class="detail-container">
        <div class="thermal-section">
           <h4>Symbols</h4>
        </div>
    <table style="width: 100%; border-collapse: collapse;">
        <tr style="background-color: #f0f2f6;">
            <th style="padding: 8px; text-align: left; border-bottom: 1px solid #ddd;">Symbol</th>
            <th style="padding: 8px; text-align: left; border-bottom: 1px solid #ddd;">Definition</th>
        </tr>
        <tr>
            <td style="padding: 8px; border-bottom: 1px solid #eee;">λ<sub>M</sub>(T)</td>
            <td style="padding: 8px; border-bottom: 1px solid #eee;"> thermal conductivity of the meter bars (reference materials) as a function of temperature, (W/(m·K))</td>
        </tr>        <tr>
            <td style="padding: 8px; border-bottom: 1px solid #eee;">λ<sub>M</sub><sup>1</sup></td>
            <td style="padding: 8px; border-bottom: 1px solid #eee;"> thermal conductivity of the upper bar, (W/(m·K))</td>
        </tr>
        <tr>
            <td style="padding: 8px; border-bottom: 1px solid #eee;">λ<sub>M</sub><sup>2</sup></td>
            <td style="padding: 8px; border-bottom: 1px solid #eee;"> thermal conductivity of the lower bar, (W/(m·K))</td>
        </tr>
        <tr>
            <td style="padding: 8px; border-bottom: 1px solid #eee;">λ<sub>S</sub>(T)</td>
            <td style="padding: 8px; border-bottom: 1px solid #eee;"> thermal conductivity of the sample corrected for heat exchanges, when necessary, (W/(m·K))</td>
        </tr>        <tr>
            <td style="padding: 8px; border-bottom: 1px solid #eee;">λ'<sub>S</sub>(T)</td>
            <td style="padding: 8px; border-bottom: 1px solid #eee;"> thermal conductivity of the sample calculated without correction for heat exchanges, (W/(m·K))</td>
        </tr>
        <tr>
            <td style="padding: 8px; border-bottom: 1px solid #eee;">λ<sub>I</sub>(T)</td>
            <td style="padding: 8px; border-bottom: 1px solid #eee;"> thermal conductivity of the insulation as a function of temperature, (W/(m·K))</td>
        </tr>
        <tr>
            <td style="padding: 8px; border-bottom: 1px solid #eee;">T</td>
            <td style="padding: 8px; border-bottom: 1px solid #eee;"> absolute temperature (K)</td>
        </tr>
        <tr>
            <td style="padding: 8px; border-bottom: 1px solid #eee;">Z</td>
            <td style="padding: 8px; border-bottom: 1px solid #eee;"> position measured from the upper end of the column, (m)</td>
        </tr>
        <tr>
            <td style="padding: 8px; border-bottom: 1px solid #eee;">l</td>
            <td style="padding: 8px; border-bottom: 1px solid #eee;"> sample length, (m)</td>
        </tr>        <tr>
            <td style="padding: 8px; border-bottom: 1px solid #eee;">T<sub>i</sub></td>
            <td style="padding: 8px; border-bottom: 1px solid #eee;"> temperature at position Z<sub>i</sub>, (K)</td>
        </tr>
        <tr>
            <td style="padding: 8px; border-bottom: 1px solid #eee;">q'</td>
            <td style="padding: 8px; border-bottom: 1px solid #eee;"> heat flux per unit area, (W/m²)</td>
        </tr>
        <tr>
            <td style="padding: 8px; border-bottom: 1px solid #eee;">δλ, δT, etc.</td>
            <td style="padding: 8px; border-bottom: 1px solid #eee;"> uncertainty in λ, T, etc.</td>
        </tr>
        <tr>
            <td style="padding: 8px; border-bottom: 1px solid #eee;">r<sub>A</sub></td>
            <td style="padding: 8px; border-bottom: 1px solid #eee;"> radius of the sample, (m)</td>
        </tr>
        <tr>
            <td style="padding: 8px; border-bottom: 1px solid #eee;">r<sub>B</sub></td>
            <td style="padding: 8px; border-bottom: 1px solid #eee;"> inner radius of the guard cylinder, (m)</td>
        </tr>
        <tr>
            <td style="padding: 8px; border-bottom: 1px solid #eee;">T<sub>g</sub>(z)</td>
            <td style="padding: 8px; border-bottom: 1px solid #eee;"> guard temperature as a function of position z, (K)</td>
        </tr>
    </table>
    </div>
    """, unsafe_allow_html=True)

# Method explanation
with st.container():
    st.markdown("""
    <div class="section-header">
        <h4>📊 The ASTM E1225 Method</h4>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1.5, 1.5, 1])
    
    col1.markdown("""
        <div class="detail-container">
            <div class="thermal-section">
                <h4>🔬 <b>Method Principles</b></h4>
            </div>
        <p>
        The <b>ASTM E1225</b> method describes a <b>steady-state</b> technique for determining the 
            <b>thermal conductivity</b> (<b>λ</b>) of <span style="color:#db7b34;"><b>homogeneous, opaque solids</b></span>.
            <br>
            <p>
                <span style="font-size: 1.1em;">&#x1F4A1; <b>This technique is applicable to materials:</b></span>
                <ul style="list-style-type: disc; padding-left: 20px;">
                    <li style="padding: 4px 0;">
                        <b>Material Type:</b> Homogeneous, opaque solids
                    </li>
                    <li style="padding: 4px 0;">
                        <b>Thermal Conductivity Range:</b> <b>0.2 &lt; λ &lt; 200 W/(m·K)</b>
                    </li>
                    <li style="padding: 4px 0;">
                        <b>Temperature Range:</b> <b>90 K &le; T &le; 1300 K</b>
                    </li>
                </ul>
                <span style="color: #388e3c;">&#x2714;&#xFE0F; <b>Key Features:</b></span>
                <ul style="list-style-type: disc; margin-left: 20px;">
                    <li>Ensures <b>high accuracy</b> for a wide range of engineering materials</li>
                    <li>Minimizes <b>heat losses</b> using a <b>guarded system</b></li>
                    <li>Relies on <b>steady-state</b> temperature gradients for precise measurement</li>
                </ul>
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    col2.markdown(""" 
        <div class="detail-container">
            <div class="thermal-section">
               <h4>📝 <b>Test Method Summary</b></h4>
            </div>
            <p>
                <b>🧩 Sample Placement:</b> A <b>test sample</b> is inserted under applied load between two <b>reference samples</b> (meter bars) of <span style="color:#db7b34;"><b>known thermal properties</b></span>. The <b>thickness</b> of these samples is chosen so that their <b>thermal conductance</b> is of similar order to that of the test sample.
            </p>
            <p>
                <b>🌡️ Temperature Gradient:</b> A <b>temperature gradient</b> is established in the test stack. <b>Heat losses</b> are minimized by using a <span style="color:#db7b34;"><b>longitudinal guard</b></span> with approximately the same temperature gradient.
            </p>
            <p>
                <b>⚖️ Equilibrium & Measurement:</b> Under <b>steady-state (equilibrium) conditions</b>, the <b>thermal conductivity</b> (<b>λ</b>) is determined from the <b>temperature gradients</b> measured in the respective samples and the <b>thermal conductivity</b> of the reference materials.
            </p>
            <ul style=" list-style-type: none; padding-left: 0; ">
                <li>🔹 <b>Reference bars:</b> Known λ<sub>M</sub></li>
                <li>🔹 <b>Test sample:</b> Unknown λ<sub>S</sub></li>
                <li>🔹 <b>Guard system:</b> Minimizes lateral heat loss</li>
                <li>🔹 <b>Accurate sensors:</b> Ensure precise gradient measurement</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.image("images/Schematic of a Comparative-Guarded-Longitudinal Heat Flow System Showing Possible Locations of Temperature Sensors.png",
                caption="Schematic representation of the GHFM method")

# System characteristics
with st.container():
    st.markdown("""
    <div class="section-header">
        <h4>⚙️ System Characteristics</h4>
    </div>
    """, unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    col1.markdown("""
    <div class="detail-container">
        <div class="thermal-section">
            <h4>🔬 <b>Applicability</b></h4>
        </div>
        <p>
            <span style="font-size: 1.1em; color: #db7b34;"><b>The comparative method</b></span> for measuring thermal conductivity is highly versatile and suitable for a broad spectrum of <b>engineering materials</b>:
        </p>
        <ul style="padding-left: 20px; margin-bottom: 0;">
            <li style="padding: 6px 0; border-bottom: 1px solid #eee;"><b>Ceramics</b> <span style="color: #888;">(e.g., insulators, tiles)</span></li>
            <li style="padding: 6px 0; border-bottom: 1px solid #eee;"><b>Polymers</b><!-- <span style="color: #888;">(plastics, composites)</span></li> -->
            <li style="padding: 6px 0; border-bottom: 1px solid #eee;"><b>Metals & Alloys</b> <span style="color: #888;">(aluminum, steel, copper, etc.)</span></li>
            <li style="padding: 6px 0; border-bottom: 1px solid #eee;"><b>Refractories</b> <span style="color: #888;">(high-temperature materials)</span></li>
            <li style="padding: 6px 0; border-bottom: 1px solid #eee;"><b>Carbons & Graphites</b></li>
            <li style="padding: 6px 0;"><b>Composite Materials</b> <span style="color: #888;">(multi-phase systems)</span></li>
        </ul>
        <p style="margin-top: 10px;">
            <span style="color: #388e3c;">&#x2714;&#xFE0F; <b>Ideal for research, quality control, and industrial applications.</b></span>
        </p>
    </div>
    """, unsafe_allow_html=True)
    col2.markdown("""
    <div class="detail-container">
        <div class="thermal-section">
            <h4>🛠️ Technical Requirements</h4>
        </div>
        <ul style="padding-left: 20px;">
            <li><b>Reference Materials:</b> Meter bars with known thermal conductivity</li>
            <li><b>Temperature Sensors:</b> Accurate sensors for measuring thermal gradient</li>
            <li><b>Control System:</b> Mechanisms to ensure steady-state conditions</li>
            <li><b>Thermal Protection:</b> Guard system to minimize heat losses</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    tech_data = {
        "Parameter": [
            "Thermal Conductivity Range", 
            "Temperature Range",
            "Typical Accuracy",
            "Sample Homogeneity",
            "Surface Finish"
        ],
        "Value": [
            "0.2 - 200 W/(m·K)", 
            "90 - 1300 K",
            "±6.8% (between 300-600 K)",
            "Variation < ±5% with thickness changes",
            "Better than 32—"
        ]
    }
    df = pd.DataFrame(tech_data)
    # Convert the dataframe to HTML and insert it into the container

    table_html = df.to_html(index=False, classes="centered-table")
    
    # Technical parameters in table format
    col3.markdown(f"""
    <div class="detail-container">
        <div class="thermal-section">
            <h4>📊 Technical Parameters</h4>
        </div>
        {table_html}
    </div>
    """, unsafe_allow_html=True)
    

    
    

# Project implementation
with st.container():
    st.markdown("""
    <div class="section-header">
        <h4>🛠️ Implementation in the GHFM Project</h4>
    </div>
    """, unsafe_allow_html=True)
    
    col_text, col_img  = st.columns([2, 1])
    
    with col_text:
        st.markdown("""
        <div class="detail-container">
            <div class="thermal-section">
            <h4> <b>Test Method Summary (ASTM E1225-20)</b> </h4>
            </div>
            <p>
            A <b>test sample</b> is inserted under applied load between two <b>meter bars</b> (reference materials) of <span style="color:#db7b34;"><b>known thermal properties</b></span> and thickness such that their <b>thermal conductance</b> is of similar order to that of the test sample. 
            <br>
            A <b>temperature gradient</b> is established in the test stack, and <span style="color:#db7b34;"><b>heat losses are minimized</b></span> by using a <b>longitudinal guard</b> with a similar temperature gradient. 
            <br>
            Under <b>steady-state (equilibrium) conditions</b>, the <b>thermal conductivity</b> (<b>λ</b>) is determined from the <b>temperature gradients</b> measured in the respective samples and the <b>thermal conductivity</b> of the reference materials.
            </p>
            <h5 style="font-weight: bold; margin-top: 15px; margin-bottom: 10px;">General Characteristics of the Method:</h5>
            <ul style="list-style-type: none; padding-left: 0;">
            <li style="padding: 8px 0; border-bottom: 1px solid #eee;">
                <b>Configuration:</b> The <b>unknown sample</b> (λ<sub>S</sub>) is mounted between two <b>meter bars</b> (λ<sub>M</sub>), all with the <b>same cross-section</b> and <b>similar thermal conductance</b> (λ/l).
            </li>
            <li style="padding: 8px 0; border-bottom: 1px solid #eee;">
                <b>Formats:</b> If bars and samples are <b>cylinders of the same diameter</b>, the method is called "<b>cut-bar</b>". For <b>flat slabs</b> (transverse dimensions &gt; thickness), it is called "<b>flat slab comparative</b>".
            </li>
            <li style="padding: 8px 0; border-bottom: 1px solid #eee;">
                <b>Thermal Contact:</b> <span style="color:#388e3c;"><b>Good contact</b></span> between surfaces is ensured by applying a <b>mechanical or pneumatic force</b>.
            </li>
            <li style="padding: 8px 0; border-bottom: 1px solid #eee;">
                <b>Insulation and Guard:</b> The assembly is <b>surrounded by insulation</b> and protected by a <b>thermal guard casing</b>, maintaining a <b>matching temperature gradient</b> to minimize lateral heat loss.
            </li>
            <li style="padding: 8px 0;">
                <b>Measurement:</b> Under <b>steady-state</b> conditions, the <b>temperature gradients</b> along the meter bars and the sample are used to calculate <b>thermal conductivity</b>.
            </li>
            </ul>
            <div style="background-color: #f8f9fa; border-left: 4px solid #db7b34; padding: 10px; margin-top: 15px;">
            <p style="font-style: italic; margin-bottom: 0;">
                <b>Note:</b> The calculation assumes <b>idealized conditions</b> with no heat exchanges between the column and insulation. In practice, <span style="color:#db7b34;"><b>careful control</b></span> and <b>additional restrictions</b> are necessary to ensure the desired accuracy.
            </p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col_img:
        st.image("images/Schematic of Typical Test Stack and Guard System Illustrating Matching of Temperature Gradients.png",
                caption="Schematic of the test system showing the matching of temperature gradients")
                
    
with st.container():
    st.markdown("""
    <div class="section-header">
        <h4>📋 Technical Details of ASTM E1225 Standard</h4>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="detail-container">
        <div class="thermal-section">
            <h4>📝 Test Procedure</h4>
        </div>
        
        ### Sample Preparation
        
        - Samples must be homogeneous (conductivity variation < ±5% with thickness changes)
        - For non-opaque systems, the combined error due to heterogeneity and photon transmission must be < ±5%
        - The radius of the sample and the meter bars must agree within ±1%
        - Surface finish must be equal to or better than 32— 
        - The normal to each end must be parallel to the sample axis within ±10 minutes
        
        ### Test Execution
        
        1. Select reference bars (meter bars) with thermal conductance of the same order of magnitude as the sample
        2. Properly instrument and install the meter bars and the sample
        3. Adjust the heaters until temperature fluctuations are < 0.03 K
        4. Adjust the power of the guard heaters to maintain a constant temperature profile (±0.1 K)
        5. After the system reaches steady state (T drift < 0.05 K/h), measure the output of all sensors
        
        </div>
        """, unsafe_allow_html=True)
   
    with col2:
        st.markdown("""
        <div class="detail-container">
            <div class="thermal-section">
                <h4>🧮 Calculations and Analysis</h4>
            </div>
        
        ### Determination of Thermal Conductivity
        
        The thermal conductivity of the specimen (λ<sub>S</sub>) is derived from the following relationship:

        λ<sub>S</sub> = λ<sub>M</sub> · [(T<sub>2</sub> - T<sub>1</sub>)/(T<sub>4</sub> - T<sub>3</sub>)] · [(Z<sub>4</sub> - Z<sub>3</sub>)/(Z<sub>2</sub> - Z<sub>1</sub>)]
        
        Where:
        - λ<sub>M</sub>: thermal conductivity of the meter bars
        - T<sub>i</sub>: temperature at position i
        - Z<sub>i</sub>: position measured from the upper end of the column
        
        ### Corrections for Stray Heat Flow
        
        For apparatus where lateral heat flow is significant, corrections are applied 
        to account for heat losses through insulation or radiation between guard 
        and test surfaces.
        
        </div>
        """, unsafe_allow_html=True)

# Applications and Examples
with st.container():
    st.markdown("""
    <div class="section-header">
        <h4>✨ Benefits of the GHFM Technique</h4>
    </div>
    """, unsafe_allow_html=True)    
    st.markdown("""
    <div class="detail-container">
        <p>The GHFM technique provides precise measurements that help in the development of new materials 
        and the improvement of industrial processes, allowing for:</p>
        <ul style=" padding-left: 0;">
            <li style="padding: 6px 0; border-bottom: 1px solid #eee;">
                <b>Optimization of energy use</b> in thermal processes
            </li>
            <li style="padding: 6px 0; border-bottom: 1px solid #eee;">
                 <b>Development of materials</b> with specific thermal properties
            </li>
            <li style="padding: 6px 0; border-bottom: 1px solid #eee;">
                <b>Validation of theoretical models</b> for heat transfer
            </li>
            <li style="padding: 6px 0;">
                <b>Quality assurance</b> in engineering materials
            </li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
        
# Advantages and limitations
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="thermal-section">
        <h4>👍 Advantages</h4>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("""
    <div class="detail-container">
        <ul style="list-style-type: none; padding-left: 0;">
            <li style="padding: 6px 0; border-bottom: 1px solid #eee;">
                ✅ High accuracy for materials within the specified range
            </li>
            <li style="padding: 6px 0; border-bottom: 1px solid #eee;">
                ✅ Well-established and standardized methodology
            </li>
            <li style="padding: 6px 0;">
                ✅ Applicable to a wide variety of materials
            </li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="thermal-section">
        <h4>👎 Limitations</h4>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("""
    <div class="detail-container">
        <ul style="list-style-type: none; padding-left: 0;">
            <li style="padding: 6px 0; border-bottom: 1px solid #eee;">
                ⚠️ Requires well-characterized reference materials
            </li>
            <li style="padding: 6px 0; border-bottom: 1px solid #eee;">
                ⚠️ Needs good thermal contact between samples
            </li>
            <li style="padding: 6px 0; border-bottom: 1px solid #eee;">
                ⚠️ Careful sample preparation is essential
            </li>
            <li style="padding: 6px 0;">
                ⚠️ Equilibrium times can be long
            </li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# References
with st.container():
    st.markdown("""
    <div class="section-header">
        <h4>📚 References</h4>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("""
    <div class="detail-container">
        <ol style="padding-left: 20px;">
            <li style="padding: 8px 0; border-bottom: 1px solid #eee;">
                <b>ASTM E1225-20</b>, "Standard Test Method for Thermal Conductivity of Solids Using the Guarded-Comparative-Longitudinal Heat Flow Technique", ASTM International, 2020.
            </li>
            <li style="padding: 8px 0; border-bottom: 1px solid #eee;">
                <b>Tye, R. P., and Hume, D.</b>, "Standards and Reference Materials for Thermal Properties Measurements," Journal of Thermal Analysis and Calorimetry, Vol 113, No. 3, 2017.
            </li>
            <li style="padding: 8px 0; border-bottom: 1px solid #eee;">
                <b>Didion, D. A.</b>, "An Analysis and Design of a Linear Guarded Cut-Bar Apparatus for Thermal Conductivity Measurements," AD-665789, January, 1968.
            </li>
            <li style="padding: 8px 0;">
                <b>Hulstrom, L. C., Tye, R. P., and Smith, S. E.</b>, "Round-Robin Testing of Thermal Conductivity Reference Materials," Thermal Conductivity 19, Yarbrough, D. W., ed., Plenum Press, New York, 1985, pp. 199–211.
            </li>
        </ol>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div class="footer">
    © 2025 GHFM Project - WEG EQUIPAMENTOS ELETRICOS S.A
</div>
""", unsafe_allow_html=True)

