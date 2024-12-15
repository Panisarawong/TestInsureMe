import pandas as pd
import streamlit as st


with open("style.css", encoding="UTF-8") as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


insurance_products = pd.read_excel('product.xlsx')

st.title("Insurance Matching System")
st.subheader("กรุณากรอกข้อมูลเพื่อค้นหาแผนประกัน")

# input
customers = {}
name = st.text_input("กรุณากรอกชื่อของคุณ ")
purpose = st.selectbox("วัตถุประสงค์ของการเดินทาง", ("ท่องเที่ยว", "เจรจาธุรกิจ", "การเรียน/ศึกษาต่อ", "อื่น ๆ"))
trip_type = st.selectbox("ประเภทประกันการเดินทางที่ต้องการ", ['รายเที่ยว', 'รายปี']) 
if trip_type == "รายเที่ยว":
    days = st.selectbox("เลือกจำนวนวันเดินทาง", [1, 3, 5, 7, 9, 14, 30, 60, 90, 120, 150, 180])
else:
    days = None 
budget_min = st.number_input("Minimum Budget (THB)", min_value=0, value=200)
budget_max = st.number_input("Maximum Budget (THB)", min_value=0, value=5000)

st.markdown("<b>กรุณาให้คะแนนความสำคัญของคุณสำหรับเงื่อนไขต่อไปนี้ (คะแนน 1-5) 1 คือ ให้ความสำคัญน้อยที่สุดและ 5 คือ ให้ความสำคัญมากที่สุด</b>", unsafe_allow_html=True)
advance_payment = st.slider("สำรองจ่ายค่ารักษาก่อน ", 1, 3, 5)
onsite_service = st.slider("เจ้าหน้าที่ให้บริการในพื้นที่ 24 ชม. ", 1, 3, 5)
online_service = st.slider("เจ้าหน้าที่ให้บริการออนไลน์ 24 ชม. ", 1, 3, 5)
baggage_coverage = st.slider("คุ้มครองกรณีกระเป๋าสูญหายหรือเสียหายทั้งไปและกลับ ", 1, 3, 5)
home_coverage = st.slider("คุ้มครองบ้านในระหว่างผู้เอาประกันภัยอยู่ต่างประเทศ ", 1, 3, 5)
flight_delay = st.slider("คุ้มครองกรณีเที่ยวบินเกิดความล่าช้า ", 1, 3, 5)
add_on_option = st.slider("สามารถซื้อประกัน Add on ได้ ", 1, 3, 5)
visa_rejection = st.slider("เงินชดเชยกรณียื่นวีซ่าไม่ผ่าน ", 1, 3, 5)

customers[name] = {
        "advance_payment": advance_payment,
        'type': trip_type,
        'budget_min': budget_min,
        'budget_max': budget_max,
        "onsite_service": onsite_service,
        "online_service": online_service,
        "baggage_coverage": baggage_coverage,
        "home_coverage": home_coverage,
        "flight_delay": flight_delay,
        "add_on_option": add_on_option,
        "visa_rejection": visa_rejection,
        "days": days
    }

# filter
if trip_type == "รายเที่ยว":
    filtered= insurance_products[
        (insurance_products['price'] >= customers[name]['budget_min']) & 
        (insurance_products['price'] <= customers[name]['budget_max']) & 
        (insurance_products['days'] == days)
    ]
else:
    filtered = insurance_products[
        (insurance_products['price'] >= customers[name]['budget_min']) & 
        (insurance_products['price'] <= customers[name]['budget_max']) & 
        (insurance_products['type'] == trip_type)
    ]


def calculate_matches(customers, filtered):
    matches = []

    for customer, c_attrs in customers.items():
        for product_index in filtered.index:
            product_coverage = filtered.loc[product_index]

            # คะแนนจากเงื่อนไข
            criteria_score = 0
            for criteria in ['advance_payment', 'onsite_service', 'online_service', 'baggage_coverage',
                             'home_coverage', 'flight_delay', 'add_on_option', 'visa_rejection']:
                if criteria in product_coverage.index:
                    criteria_score += c_attrs[criteria] * product_coverage[criteria]

            # รวมคะแนนทั้งหมด 
            total_score = criteria_score
            
            # เพิ่มผลลัพธ์พร้อมคะแนน
            matches.append((customer, product_index, total_score))

    # จัดเรียงตามคะแนน (จากมากไปน้อย)
    matches = sorted(matches, key=lambda x: x[2], reverse=True)
    
    return matches

# แสดงผลลัพธ์
if st.button("ค้นหาประกันที่เหมาะสม"):
    if filtered.empty:
        st.write("ไม่พบประกันที่เหมาะกับคุณ กรุณากรอกข้อมูลใหม่อีกครั้ง")
    else:
        matches = calculate_matches(customers, filtered)

        if not matches:
            st.write("ไม่พบประกันที่เหมาะกับคุณ กรุณากรอกข้อมูลใหม่อีกครั้ง")
        else:
            st.write("\n### แผนประกันการเดินทางที่เหมาะกับคุณ")
            cols = st.columns(3)
            top_3_matches = matches[:3] 

            for i, (customer, product_index, score) in enumerate(top_3_matches):
                product_name = filtered.loc[product_index, 'name']
                price = filtered.loc[product_index, 'price']
                type = filtered.loc[product_index, 'type']

                with cols[i]:  
                    st.markdown(f"""
                        <div>
                            <h5>{product_name}</h5>
                            <p>ประกันการเดินทาง <b>{type} </b></p>
                            <p>ค่าเบี้ยประกัน <b> {price} บาท</b></p>
                            <p>คะแนนความเหมาะสม <b>{score:.2f}</b></p>
                        </div>
                    """, unsafe_allow_html=True)

            # top_3_matches = matches[:3]  # เลือกเฉพาะ 3 อันดับแรก
            # for i, (customer, product_index, score) in enumerate(top_3_matches, start=1):
            #     product_name = filtered.loc[product_index, 'name']
            #     price = filtered.loc[product_index, 'price']
            #     st.write(f"{i}.คุณ {name} เหมาะกับประกัน {product_name} ค่าเบี้ยประกัน {price} บาท (คะแนน: {score:.2f})")


# st.write("Filtered Data:", filtered)
# # แสดงผลลัพธ์
# if st.button("ค้นหาประกันที่เหมาะสม"):
#     if filtered.empty:
#         st.write("ไม่พบประกันที่เหมาะกับคุณ กรุณากรอกข้อมูลใหม่อีกครั้ง")
#     else:
#         matches = calculate_matches(customers, filtered)

#         if not matches:
#             st.write("ไม่พบประกันที่เหมาะกับคุณ กรุณากรอกข้อมูลใหม่อีกครั้ง")
#         else:
#             st.write("\n### แผนประกันการเดินทางที่เหมาะกับคุณ:")
#             top_3_matches = matches[:3]  # เลือกเฉพาะ 3 อันดับแรก
#             for i, (customer, product_index, score) in enumerate(top_3_matches, start=1):
#                 product_name = filtered.loc[product_index, 'name']
#                 price = filtered.loc[product_index, 'price']
#                 st.write(f"{i}. {product_name} ค่าเบี้ยประกัน {price} บาท (คะแนน: {score:.2f})")



# def calculate_matches(customers, filtered):
#     G = nx.Graph()  # สร้างกราฟ Bipartite
#     matches = []

#     # สร้างโหนดสำหรับลูกค้าและแผนประกันในกราฟ
#     for customer in customers:
#         G.add_node(customer, bipartite=0)  # กลุ่มลูกค้า
#     for product_index in filtered.index:
#         G.add_node(product_index, bipartite=1)  # กลุ่มแผนประกัน

#     # คำนวณคะแนนและเพิ่มขอบ (edge) ระหว่างลูกค้าและแผนประกัน
#     for customer, c_attrs in customers.items():
#         for product_index in filtered.index:
#             product_coverage = filtered.loc[product_index]

#             # คะแนนจากเงื่อนไขต่างๆ
#             criteria_score = 0
#             for criteria in ['advance_payment', 'onsite_service', 'online_service', 'baggage_coverage',
#                              'home_coverage', 'flight_delay', 'add_on_option', 'visa_rejection']:
#                 if criteria in product_coverage.index:
#                     criteria_score += c_attrs[criteria] * product_coverage[criteria]

#             # เพิ่มขอบระหว่างลูกค้าและแผนประกันพร้อมคะแนน
#             G.add_edge(customer, product_index, weight=criteria_score)

#     # ทำการจับคู่ Bipartite Matching
#     matches = nx.bipartite.maximum_matching(G)

#     # สร้างรายการผลลัพธ์จากการจับคู่
#     result = []
#     for customer in customers:
#         # หาแผนประกันที่จับคู่กับลูกค้า
#         if customer in matches:
#             product_index = matches[customer]
#             # ตรวจสอบว่าเป็นแผนประกัน
#             if isinstance(product_index, str):  # ตรวจสอบว่าเป็นแผนประกันจริงๆ
#                 product_coverage = filtered.loc[product_index]
#                 criteria_score = 0
#                 for criteria in ['advance_payment', 'onsite_service', 'online_service', 'baggage_coverage',
#                                  'home_coverage', 'flight_delay', 'add_on_option', 'visa_rejection']:
#                     if criteria in product_coverage.index:
#                         criteria_score += customers[customer][criteria] * product_coverage[criteria]

#                 total_score = criteria_score
#                 result.append((customer, product_index, total_score))

#     # จัดเรียงตามคะแนน (จากมากไปน้อย)
#     result = sorted(result, key=lambda x: x[2], reverse=True)
    
#     return result

# # แสดงผลลัพธ์
# if st.button("ค้นหาประกันที่เหมาะสม"):
#     if filtered.empty:
#         st.write("ไม่พบประกันที่เหมาะกับคุณ กรุณากรอกข้อมูลใหม่อีกครั้ง")
#     else:
#         matches = calculate_matches(customers, filtered)

#         if not matches:
#             st.write("ไม่พบประกันที่เหมาะกับคุณ กรุณากรอกข้อมูลใหม่อีกครั้ง")
#         else:
#             st.write("\n### แผนประกันการเดินทางที่เหมาะกับคุณ:")
#             top_3_matches = matches[:3]  # เลือกเฉพาะ 3 อันดับแรก
#             for i, (customer, product_index, score) in enumerate(top_3_matches, start=1):
#                 product_name = filtered.loc[product_index, 'name']
#                 st.write(f"{i}. {product_name} (คะแนน: {score:.2f})")






# def calculate_matches(customers, filtered):
#     matches = []

#     for customer, c_attrs in customers.items():
#         for product_index in filtered.index:
#             product_coverage = filtered.loc[product_index]

#             # คะแนนจากเงื่อนไข
#             criteria_score = 0
#             for criteria in ['advance_payment', 'onsite_service', 'online_service', 'baggage_coverage',
#                              'home_coverage', 'flight_delay', 'add_on_option', 'visa_rejection']:
#                 if criteria in product_coverage.index:
#                     criteria_score += c_attrs[criteria] * product_coverage[criteria]

#             # รวมคะแนนทั้งหมด 
#             total_score = criteria_score

#             # เพิ่มผลลัพธ์พร้อมคะแนน
#             matches.append((customer, product_index, total_score))

#     # จัดเรียงตามคะแนน (จากมากไปน้อย)
#     matches = sorted(matches, key=lambda x: x[2], reverse=True)
#     return matches

# # แสดงผลลัพธ์
# if st.button("ค้นหาประกันที่เหมาะสม"):
#     if filtered.empty:
#         st.write("ไม่พบประกันที่เหมาะกับคุณ กรุณากรอกข้อมูลใหม่อีกครั้ง")
#     else:
#         matches = calculate_matches(customers, filtered)

#         if not matches:
#             st.write("ไม่พบประกันที่เหมาะกับคุณ กรุณากรอกข้อมูลใหม่อีกครั้ง")
#         else:
#             st.write("\n### แผนประกันการเดินทางที่เหมาะกับคุณ:")
#             top_3_matches = matches[:3]  # เลือกเฉพาะ 3 อันดับแรก
#             for i, (customer, product_index, score) in enumerate(top_3_matches, start=1):
#                 product_name = filtered.loc[product_index, 'name']
#                 st.write(f"{i}. {product_name} (คะแนน: {score:.2f})")




# # แก้ไขการแสดงผลให้เป็น Top 3
# def calculate_matches(customers, filtered):
#     matches = []

#     for customer, c_attrs in customers.items():
#         for product_index in filtered.index:
#             product_coverage = filtered.loc[product_index]

#             # คะแนนจากงบประมาณ (Budget)
#             price_weight = 5  # น้ำหนักสำหรับงบประมาณ
#             price_diff = abs((c_attrs['budget_min'] + c_attrs['budget_max']) / 2 - product_coverage['price'])
#             budget_score = (1 / (1 + price_diff)) * price_weight

#             # คะแนนจากคุณสมบัติ (Criteria)
#             criteria_score = 0
#             for criteria in ['advance_payment', 'onsite_service', 'online_service', 'baggage_coverage',
#                              'home_coverage', 'flight_delay', 'add_on_option', 'visa_rejection']:
#                 if criteria in product_coverage.index:
#                     criteria_score += c_attrs[criteria] * product_coverage[criteria]

#             # รวมคะแนนทั้งหมด
#             total_score = budget_score + criteria_score

#             # เพิ่มผลลัพธ์พร้อมคะแนน
#             matches.append((customer, product_index, total_score))

#     # จัดเรียงตามคะแนน (จากมากไปน้อย)
#     matches = sorted(matches, key=lambda x: x[2], reverse=True)
#     return matches

# # แสดงผลลัพธ์
# if st.button("Find Best Match"):
#     if filtered.empty:
#         st.write("ไม่พบประกันที่เหมาะกับคุณ กรุณากรอกข้อมูลใหม่อีกครั้ง")
#     else:
#         matches = calculate_matches(customers, filtered)

#         if not matches:
#             st.write("ไม่พบประกันที่เหมาะกับคุณ กรุณากรอกข้อมูลใหม่อีกครั้ง")
#         else:
#             st.write("\n## Result (Top 3):")
#             top_3_matches = matches[:3]  # เลือกเฉพาะ 3 อันดับแรก
#             for i, (customer, product_index, score) in enumerate(top_3_matches, start=1):
#                 product_name = filtered.loc[product_index, 'name']
#                 st.write(f"{i}. คุณ {customer} เหมาะสมกับประกัน {product_name} (คะแนน: {score:.2f})")







# def calculate_matches(customers, insurance_products):
#     B = nx.Graph()
#     top_matches = []

#     for customer, c_attrs in customers.items():
#         max_score = 0
#         best_product = None
#         for product_index in insurance_products.index:
#             product_coverage = insurance_products.loc[product_index]
#             score = sum(c_attrs[criteria] * product_coverage[criteria] for criteria in c_attrs.keys())
            
#             if score > max_score:
#                 max_score = score
#                 best_product = product_index
            
#             # เพิ่มขอบในกราฟ
#             B.add_edge(customer, product_index, weight=score)
        
#         # save the highest score
#         if best_product is not None:
#             top_matches.append((customer, best_product, max_score))
    
#     return top_matches

# # result
# if st.button("Find Best Match"):
#     top_matches = calculate_matches(customers, insurance_products)

#     st.write("\n## Result:")
#     for customer, product_index, score in top_matches:
#         product_name = insurance_products.loc[product_index, 'name']
#         st.write(f"{customer} is matched with {product_name} (Score: {score})")



