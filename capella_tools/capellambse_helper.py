#capellmbse_helper
import capellambse
import pandas as pd 
from IPython.display import Markdown

from IPython.core.display import HTML
from IPython import display
import pandas as pd 
import jinja2


def filter_property_value(value):
    """
    Process a property value to return a clean representation suitable for Jinja reports.
    
    Handles enumeration values, floats, and strings appropriately.
    
    :param value: The property value, which can be an enumeration, float, or string.
    :return: A cleaned representation of the property value.
    """
    if isinstance(value, list):
        # Handle enumeration property values (assumed to be a list of indices or objects)
        return ", ".join(str(v) for v in value)
    elif isinstance(value, (int, float)):
        return f"{value:.2f}" if isinstance(value, float) else str(value)
    elif isinstance(value, str):
        return value.strip()
    elif hasattr(value, "name"):
        # If it's an object with a 'name' attribute (potentially an enumeration literal)
        return value.name
    else:
        return "Unknown"



def display_context_diagram(obj):
    if obj.__class__.__name__ == "Entity" or \
        obj.__class__.__name__ == "OperationalActivity" or \
        obj.__class__.__name__ == "OperationalCapability" or \
        obj.__class__.__name__ == "Mission" or \
        obj.__class__.__name__ == "Capability" or \
        obj.__class__.__name__ == "SystemFunction" or \
        obj.__class__.__name__ == "LogicalComponent" or \
        obj.__class__.__name__ == "ComponentExchange" or \
        obj.__class__.__name__ == "LogicalFunction" or \
        obj.__class__.__name__ == "FunctionalExchange" or \
        obj.__class__.__name__ == "PhysicalComponent" or \
        obj.__class__.__name__ == "PhysicalFunction" :
        display.display(obj.context_diagram)
    else :
        display.display(Markdown(f"The object:{obj.name} cannot be displayed in a Context Diagram."))
        
    
def Display_Logical_Functional_Chain_Tables(fc):
    #print(fc)
    #print()
    #print("Functional Chain:", fc.name)
    display.display(Markdown(f"# Functional Chain: {fc.name}"))
    
    
    df = pd.DataFrame({
    'Function Owner': [],
    'Function': [],
    'Function Exchange': [],
    'Function Exchange Items': [],
    'Function Exchange Item Elements': [],
    })
    def Append_Row_to_Dataframe(df,  Current_Function_Owner ,Current_Function,\
                               Current_Function_Exchange , Current_Function_Exchange_EI, Current_Function_Exchange_EIE) :
        print("appending")
        df.loc[len(df)] = [Current_Function_Owner ,Current_Function,\
                                Current_Function_Exchange , Current_Function_Exchange_EI, Current_Function_Exchange_EIE]
        
    for function in fc.involved_functions:
        #This will initialize all the table elements
        Current_Function_Owner = ''
        Current_Function =''
        Current_Function_Exchange = ''
        Current_Function_Exchange_EI = ''
        Current_Function_Exchange_EIE = ''
        
        #print(function.owner)
        if function.owner != None :
         
            Current_Function_Owner=function.owner.name
            #print("- Entity:",Current_Function_Owner)
            #print("-Function:",function.name)
            Current_Function = function.name
            #print("-Function:",Current_Function)
           
            
            #print("---Exch:",exchange.name)
            if function.outputs :
                for output in function.outputs:
                   # print(output)
                    is_FOs= True
                    Current_Function_OPort = output.name
                    #Append_Row_to_Dataframe(df,  Current_Function_Owner ,Current_Function,\
                    #                 Current_Function_Exchange , Current_Function_Exchange_EI, Current_Function_Exchange_EIE)
                    for exchange in output.exchanges:         
                        for involved_exchange in fc.involved_links:
                             if exchange == involved_exchange:
                                 Current_Function_Exchange = exchange.name
                                 #print("--Output:",output.name)
                                 #print("---Exch:",Current_Function_Exchange)
                                 
                                 for exchange_item in exchange.exchange_items: 
                                     Current_Function_Exchange_EI = exchange_item.name
                                     #print("--Output:",output.name)
                                     #print(exchange_item)
                                     #print("---Exch Item:",Current_Function_Exchange_EI)
        
                                     for element in exchange_item.elements: 
                                         Current_Function_Exchange_EIE = element.name
                                         #print(element)
                                         #print("---Exch Item Elements:",Current_Function_Exchange_EIE)
                                         Append_Row_to_Dataframe(df,  Current_Function_Owner ,Current_Function,\
                                            Current_Function_Exchange , Current_Function_Exchange_EI, Current_Function_Exchange_EIE)
                                     if  exchange_item.elements ==  []:
                                         Append_Row_to_Dataframe(df,  Current_Function_Owner ,Current_Function,\
                                        Current_Function_Exchange , Current_Function_Exchange_EI, Current_Function_Exchange_EIE) 
                                 if exchange.exchange_items == [] :
                                    Append_Row_to_Dataframe(df,  Current_Function_Owner ,Current_Function,\
                                    Current_Function_Exchange , Current_Function_Exchange_EI, Current_Function_Exchange_EIE) 
            else: 
                Append_Row_to_Dataframe(df,  Current_Function_Owner ,Current_Function,\
                                Current_Function_Exchange , Current_Function_Exchange_EI, Current_Function_Exchange_EIE)
          
        else: 
            Current_Function_Owner="None"
            print("-Entity","None")
            Current_Function = function.name
            print("-Function",Current_Function )
            if function.outputs :
                for output in function.outputs:  
                    Current_Function_OPort = output.name
                    Current_Function_OPort = output.name
                    #Append_Row_to_Dataframe(df,  Current_Function_Owner ,Current_Function,\
                    #    Current_Function_Exchange , Current_Function_Exchange_EI, Current_Function_Exchange_EIE)
                    for exchange in output.exchanges:
                       for involved_exchange in fc.involved_links:
                             if exchange == involved_exchange:
                                 
                                 
                                 Current_Function_Exchange = exchange.name
                                 #print("--Output:",output.name)
                                 #print("---Exch:",Current_Function_Exchange)
                                 if exchange.exchange_items == [] :
                                     Append_Row_to_Dataframe(df,  Current_Function_Owner ,Current_Function,\
                                     Current_Function_Exchange , Current_Function_Exchange_EI, Current_Function_Exchange_EIE)   
                                 for exchange_item in exchange.exchange_items: 
                                     Current_Function_Exchange_EI = exchange_item.name
                                     #print("--Output:",output.name)
                                     #print(exchange_item)
                                     #print("---Exch Item:",Current_Function_Exchange_EI)
                                     
                                     
                                     for element in exchange_item.elements: 
                                         Current_Function_Exchange_EIE = element.name
                                         #print(element)
                                         #print("---Exch Item Elements:",Current_Function_Exchange_EIE)
                                         Append_Row_to_Dataframe(df,  Current_Function_Owner ,Current_Function,\
                                           Current_Function_Exchange , Current_Function_Exchange_EI, Current_Function_Exchange_EIE)
                                     if exchange_item.elements == []:
                                         Append_Row_to_Dataframe(df,  Current_Function_Owner ,Current_Function,\
                                        Current_Function_Exchange , Current_Function_Exchange_EI, Current_Function_Exchange_EIE) 
                                 if exchange.exchange_items == [] :
                                     Append_Row_to_Dataframe(df,  Current_Function_Owner ,Current_Function,\
                                     Current_Function_Exchange , Current_Function_Exchange_EI, Current_Function_Exchange_EIE)    
                               
                                                           
            else: 
                Append_Row_to_Dataframe(df,  Current_Function_Owner ,Current_Function,\
                                Current_Function_Exchange , Current_Function_Exchange_EI, Current_Function_Exchange_EIE)
    
    
    display.display(df)


#Monkey Patch to constraint class to extract stipped text without hyper links.
from bs4 import BeautifulSoup   
def strip_html_tags(text):
    soup = BeautifulSoup(text, "html.parser")
    return soup.get_text()
def spectext(self):
   
    return strip_html_tags(str(self.specification))
    
capellambse.metamodel.capellacore.Constraint.spectext = spectext

def display_function_property_values(model):
    df = pd.DataFrame({
        'Logical Function': [],
        'Property Value Group Name': [],
        'Propery Name': [],
        'Property Value': [],
        })
    
    for function in model.all_functions:
        for pvg in  function.applied_property_value_groups :
            for pv in  pvg.property_values:
                #print("LogicalFunction=",'"' +function.name+ '"',"property_value_groups=",'"' +pvg.name+ '"','"Property Name"=','"' +pv.name+ '"','"Value"=',pv.value )
                df.loc[len(df)] = [function.name,pvg.name,\
                                    pv.name, pv.value]
    display(df)

def display_component_property_values(model):
    df = pd.DataFrame({
        'Logical Component': [],
        'Property Value Group Name': [],
        'Property Name': [],
        'Property Value': [],
        })
    for component in model.all_components:
        for pvg in  component.applied_property_value_groups :
            for pv in  pvg.property_values:
                #print("LogicalComponents=",'"' +component.name+ '"',"property_value_groups=",'"' +pvg.name+ '"','Property Name=','"' + pv.name + '"','Value=',pv.value  )
                df.loc[len(df)] = [component.name,pvg.name,\
                                    pv.name, pv.value]
    display(df)




def display_function_constraints(model) :
    df = pd.DataFrame({
        'Logical Function': [],
        'Constraint Index':[],
        'Constraint': [],
        })
    
    for function in model.all_functions:
        index = 0
        for constraint in function.constraints:
            df.loc[len(df)] = [function.name,\
                                    index,\
                                    constraint.spectext()]
            index = index +1
    pd.set_option('display.max_colwidth', 200)  # Set the maximum column width
    display(df)

def display_component_constraints(model):
    df = pd.DataFrame({
        'Logical Component': [],
        'Constraint Index':[],
        'Constraint': [],
        })
    for component in model.all_components:
        index = 0
        for constraint in component.constraints:
            df.loc[len(df)] = [component.name,\
                                   index,\
                                   constraint.spectext]
            index = index +1
    pd.set_option('display.max_colwidth', 200)  # Set the maximum column width
    
    display(df)



def Generate_Operational_Process_Report(op):
    templ = """
    <h1 style= "padding-left: 0"style= "padding-left: 0">Operational Process: {{ op.name }} - <span style="font-size: 10px" > UUID: {{ op.uuid }} </span> </h1>
     {% if op.summary %}
        <p><b>Summary:</b>{{ op.summary }}</p>
    {% endif %}
    {% if op.description %}
        <p><b>Description</b></p>
        <!-- Description contains preformatted HTML content -->
        <div>{{ op.description | safe }}</div>
     {% endif %}
    {% if op.applied_property_values %}
    <p  >The table below identifies property values of {{ op.name }}.</p>
        <table  style="border: 2px solid black; width:100% " >
            <tr>
                <th style="text-align:left ;border: 1px solid black" >Property Name </th>
                <th style="text-align:left ; border: 1px solid black">Property Value</th>
            </tr>
           {% for pv in node.applied_property_values %}
            <tr>
                <td style="text-align:left ; border: 1px solid black">{{ pv.name }}</td>
                <td style="text-align:left ; border: 1px solid black">{{ pv.value }}</td>
            </tr>
          {% endfor %}
           </table>
         <p style="text-align: center;"><strong>Property Values of {{ op.name }}</strong></p>
    {% else %}
        <!--<p style="text-align: left;">No extension applied property values.</p>-->
    {% endif %}   
    {% if op.applied_property_value_groups %}
    <p  >The table below identifies property values groups of {{ op.name }}.</p>
        <table  style="border: 2px solid black; width:100% " >
            <tr>
                <th style="text-align:left ;border: 1px solid black" >Property Group Name </th>
                <th style="text-align:left ; border: 1px solid black">Property Summary</th>
            </tr>
            {% set pvgs = op.applied_property_value_groups %}

               {% for pvg in pvgs  %}
                <tr>
                    <td style="text-align:left ; border: 1px solid black">{{ pvg.name }}</td>
                    <td style="text-align:left ; border: 1px solid black">{{ pvg.summary }}</td>
                </tr>
                <tr>
                    <td style="text-align:right ; border: 1px solid black"> Properties of {{ pvg.name  }}</td>
                    <td style="text-align:left ; border: 1px solid black"> 
                            <table  style="border: 1px solid black; width:100% " >
                                <tr>
                                    <th style="text-align:left ;border: 1px solid black">Property Name  </th>
                                    <th style="text-align:left ; border: 1px solid black"> Property Value </th>
                                </tr>
                            {% for pvs in pvg.property_values %}
                            <tr>
                                <td style="text-align:left ; border: 1px solid black">{{ pvs.name }} </td>
                                <td style="text-align:left ; border: 1px solid black">{{ filter_property_value(pvs.value) }}</td>
                            </tr>
                           {% endfor %}
                           </table>

                  </td>
                </tr>
               {% endfor %}

           </table>
         <p style="text-align: center;"><strong>Property Values Groups {{ op.name }}</strong></p>
    {% else %}
        <!--<p style="text-align: left;">No extension applied property values groups.</p>-->
    {% endif %}
    """
    return templ

def Generate_Functional_Chain_Report(op):
    templ = """
    <h1 style= "padding-left: 0"style= "padding-left: 0">Functional Chain: {{ op.name }} - <span style="font-size: 10px" > UUID: {{ op.uuid }} </span> </h1>
     {% if op.summary %}
        <p><b>Summary:</b>{{ op.summary }}</p>
    {% endif %}
    {% if op.description %}
        <p><b>Description</b></p>
        <!-- Description contains preformatted HTML content -->
        <div>{{ op.description | safe }}</div>
     {% endif %}
    {% if op.applied_property_values %}
    <p  >The table below identifies property values of {{ op.name }}.</p>
        <table  style="border: 2px solid black; width:100% " >
            <tr>
                <th style="text-align:left ;border: 1px solid black" >Property Name </th>
                <th style="text-align:left ; border: 1px solid black">Property Value</th>
            </tr>
           {% for pv in node.applied_property_values %}
            <tr>
                <td style="text-align:left ; border: 1px solid black">{{ pv.name }}</td>
                <td style="text-align:left ; border: 1px solid black">{{ pv.value }}</td>
            </tr>
          {% endfor %}
           </table>
         <p style="text-align: center;"><strong>Property Values of {{ op.name }}</strong></p>
    {% else %}
        <!--<p style="text-align: left;">No extension applied property values.</p>-->
    {% endif %}   
    {% if op.applied_property_value_groups %}
    <p  >The table below identifies property values groups of {{ op.name }}.</p>
        <table  style="border: 2px solid black; width:100% " >
            <tr>
                <th style="text-align:left ;border: 1px solid black" >Property Group Name </th>
                <th style="text-align:left ; border: 1px solid black">Property Summary</th>
            </tr>
            {% set pvgs = op.applied_property_value_groups %}

               {% for pvg in pvgs  %}
                <tr>
                    <td style="text-align:left ; border: 1px solid black">{{ pvg.name }}</td>
                    <td style="text-align:left ; border: 1px solid black">{{ pvg.summary }}</td>
                </tr>
                <tr>
                    <td style="text-align:right ; border: 1px solid black"> Properties of {{ pvg.name  }}</td>
                    <td style="text-align:left ; border: 1px solid black"> 
                            <table  style="border: 1px solid black; width:100% " >
                                <tr>
                                    <th style="text-align:left ;border: 1px solid black">Property Name  </th>
                                    <th style="text-align:left ; border: 1px solid black"> Property Value </th>
                                </tr>
                            {% for pvs in pvg.property_values %}
                            <tr>
                                <td style="text-align:left ; border: 1px solid black">{{ pvs.name }} </td>
                                <td style="text-align:left ; border: 1px solid black">{{ pvs.value }}</td>
                            </tr>
                           {% endfor %}
                           </table>

                  </td>
                </tr>
               {% endfor %}

           </table>
         <p style="text-align: center;"><strong>Property Values Groups {{ op.name }}</strong></p>
    {% else %}
        <!--<p style="text-align: left;">No extension applied property values groups.</p>-->
    {% endif %}
    """
    return templ

def Generate_Function_Report(oa):
    templ = """
    <h2 style= "padding-left: 0"style= "padding-left: 0">Function: {{ oa.name }} - <span style="font-size: 10px" > UUID: {{ oa.uuid }} </span> </h2>
    {% if oa.summary %}
        <p><b>Summary:</b>{{ oa.summary }}</p>
    {% endif %}
    <p><b>Owning Component or Actor:</b>  {{ oa.owner.name if oa.owner.name else "none" }}</p>
    {% if oa.description %}
        <p><b>Description</b></p>
        <!-- Description contains preformatted HTML content -->
        <div>{{ oa.description | safe }}</div>
     {% endif %}
    {% if oa.applied_property_values %}
    <p  >The table below identifies property values of {{ oa.name }}.</p>
        <table  style="border: 2px solid black; width:100% " >
            <tr>
                <th style="text-align:left ;border: 1px solid black" >Property Name </th>
                <th style="text-align:left ; border: 1px solid black">Property Value</th>
            </tr>
           {% for pv in node.applied_property_values %}
            <tr>
                <td style="text-align:left ; border: 1px solid black">{{ pv.name }}</td>
                <td style="text-align:left ; border: 1px solid black">{{ pv.value }}</td>
            </tr>
          {% endfor %}
           </table>
         <p style="text-align: center;"><strong>Property Values of {{ oa.name }}</strong></p>
    {% else %}
        <!--<p style="text-align: left;">No extension applied property values.</p>-->
    {% endif %}   
    {% if oa.applied_property_value_groups %}
    <p  >The table below identifies property values groups of {{ oa.name }}.</p>
        <table  style="border: 2px solid black; width:100% " >
            <tr>
                <th style="text-align:left ;border: 1px solid black" >Property Group Name </th>
                <th style="text-align:left ; border: 1px solid black">Property Summary</th>
            </tr>
            {% set pvgs = oa.applied_property_value_groups %}

               {% for pvg in pvgs %}
                <tr>
                    <td style="text-align:left ; border: 1px solid black">{{ pvg.name }}</td>
                    <td style="text-align:left ; border: 1px solid black">{{ pvg.summary }}</td>
                </tr>
                <tr>
                    <td style="text-align:right ; border: 1px solid black"> Properties of {{ pvg.name  }}</td>
                    <td style="text-align:left ; border: 1px solid black"> 
                            <table  style="border: 1px solid black; width:100% " >
                                <tr>
                                    <th style="text-align:left ;border: 1px solid black">Property Name  </th>
                                    <th style="text-align:left ; border: 1px solid black"> Property Value </th>
                                </tr>
                            {% for pvs in pvg.property_values %}
                            <tr>
                                <td style="text-align:left ; border: 1px solid black">{{ pvs.name }} </td>
                                <td style="text-align:left ; border: 1px solid black">{{ filter_property_value(pvs.value) }}</td>
                            </tr>
                           {% endfor %}
                           </table>

                  </td>
                </tr>
               {% endfor %}

           </table>
         <p style="text-align: center;"><strong>Property Values Groups {{ oa.name }}</strong></p>
    {% else %}
        <!--<p style="text-align: left;">No extension applied property values groups.</p>-->
    {% endif %}
    """
    return templ


def Generate_Operational_Activity_Report(oa):
    templ = """
    <h2 style= "padding-left: 0"style= "padding-left: 0">OA: {{ oa.name }} - <span style="font-size: 10px" > UUID: {{ oa.uuid }} </span> </h2>
    {% if oa.summary %}
        <p><b>Summary:</b>{{ oa.summary }}</p>
    {% endif %}
    <p><b>Owning Entity or Actor:</b>  {{ oa.owner.name if oa.owner.name else "none" }}</p>
    {% if oa.description %}
        <p><b>Description</b></p>
        <!-- Description contains preformatted HTML content -->
        <div>{{ oa.description | safe }}</div>
     {% endif %}
    {% if oa.applied_property_values %}
    <p  >The table below identifies property values of {{ oa.name }}.</p>
        <table  style="border: 2px solid black; width:100% " >
            <tr>
                <th style="text-align:left ;border: 1px solid black" >Property Name </th>
                <th style="text-align:left ; border: 1px solid black">Property Value</th>
            </tr>
           {% for pv in node.applied_property_values %}
            <tr>
                <td style="text-align:left ; border: 1px solid black">{{ pv.name }}</td>
                <td style="text-align:left ; border: 1px solid black">{{ pv.value }}</td>
            </tr>
          {% endfor %}
           </table>
         <p style="text-align: center;"><strong>Property Values of {{ oa.name }}</strong></p>
    {% else %}
        <!--<p style="text-align: left;">No extension applied property values.</p>-->
    {% endif %}   
    {% if oa.applied_property_value_groups %}
    <p  >The table below identifies property values groups of {{ oa.name }}.</p>
        <table  style="border: 2px solid black; width:100% " >
            <tr>
                <th style="text-align:left ;border: 1px solid black" >Property Group Name </th>
                <th style="text-align:left ; border: 1px solid black">Property Summary</th>
            </tr>
            {% set pvgs = oa.applied_property_value_groups %}

               {% for pvg in pvgs %}
                <tr>
                    <td style="text-align:left ; border: 1px solid black">{{ pvg.name }}</td>
                    <td style="text-align:left ; border: 1px solid black">{{ pvg.summary }}</td>
                </tr>
                <tr>
                    <td style="text-align:right ; border: 1px solid black"> Properties of {{ pvg.name  }}</td>
                    <td style="text-align:left ; border: 1px solid black"> 
                            <table  style="border: 1px solid black; width:100% " >
                                <tr>
                                    <th style="text-align:left ;border: 1px solid black">Property Name  </th>
                                    <th style="text-align:left ; border: 1px solid black"> Property Value </th>
                                </tr>
                            {% for pvs in pvgs.property_values %}
                            <tr>
                                <td style="text-align:left ; border: 1px solid black">{{ pvs.name }} </td>
                                <td style="text-align:left ; border: 1px solid black">{{ pvs.value }}</td>
                            </tr>
                           {% endfor %}
                           </table>

                  </td>
                </tr>
               {% endfor %}

           </table>
         <p style="text-align: center;"><strong>Property Values Groups {{ oa.name }}</strong></p>
    {% else %}
        <!--<p style="text-align: left;">No extension applied property values groups.</p>-->
    {% endif %}
    """
    return templ

def Generate_Operational_Capability_Report(oc):
    templ = """
    <h2 style= "padding-left: 0"style= "padding-left: 0">OC: {{ oc.name }} - <span style="font-size: 10px" > UUID: {{ oc.uuid }} </span> </h2>
    {% if oc.summary %}
        <p><b>Summary:</b>{{ oc.summary }}</p>
    {% endif %}

    {% if oc.description %}
        <p><b>Capability Description</b></p>
        <!-- Description contains preformatted HTML content -->
        <div>{{ oc.description | safe }}</div>
     {% endif %}
    <p style="text-align: left;"><strong>Involved Entities: </strong></p>
    {% set invents = oc.involved_entities %}
    {% for invent in invents %}
        <p style= "padding-left: 0"style= "padding-left: 0">{{ invent.name }} - <span style="font-size: 10px" > UUID: {{ invent.uuid }} </span> </p>
        {% if invent.summary %}
            <p>{{ invent.name }} Summary:{{ invent.summary }}</p>
        {% endif %}
        <!--{% if invent.description %} -->
           <!-- <p>{{ invent.name }} Description:</p> -->
            <!-- Description contains preformatted HTML content -->
           <!-- <div>{{ invent.description | safe }}</div> -->
       <!-- {% endif %} -->

    {% endfor %}
    <p style="text-align: left;"><strong>Involved Processes: </strong></p>
    {% set invprocs = oc.involved_processes %}
    {% for invproc in invprocs %}
        <p style= "padding-left: 0"style= "padding-left: 0">{{ invproc.name }} - <span style="font-size: 10px" > UUID: {{ invproc.uuid }} </span> </p>
        {% if invproc.summary %}
            <p><b>{{ invproc.name }} Summary:</b>{{ invproc.summary }}</p>
        {% endif %}
         <!--   {% if invproc.description %}-->
         <!--   <p>{{ invproc.name }} Description:</p>-->
            <!-- Description contains preformatted HTML content -->
         <!--   <div>{{ invproc.description | safe }}</div>-->
         <!--{% endif %}-->

    {% endfor %}
    {% if oc.applied_property_values %}
    <p style="text-align: left;"><strong> Applied Properties </strong></p> 
    <p  >The table below identifies property values of {{ oc.name }}.</p>
        <table  style="border: 2px solid black; width:100% " >
            <tr>
                <th style="text-align:left ;border: 1px solid black" >Property Name </th>
                <th style="text-align:left ; border: 1px solid black">Property Value</th>
            </tr>
           {% for pv in node.applied_property_values %}
            <tr>
                <td style="text-align:left ; border: 1px solid black">{{ pv.name }}</td>
                <td style="text-align:left ; border: 1px solid black">{{ pv.value }}</td>
            </tr>
          {% endfor %}
           </table>
         <p style="text-align: center;"><strong>Property Values of {{ oc.name }}</strong></p>
    {% else %}
        <!--<p style="text-align: left;">No extension applied property values.</p>-->
    {% endif %}   
    {% if oc.applied_property_value_groups %}
    <p style="text-align: left;"><strong> Applied Property Groups</strong></p> 
    <p  >The table below identifies property values groups of {{ oc.name }}.</p>
        <table  style="border: 2px solid black; width:100% " >
            <tr>
                <th style="text-align:left ;border: 1px solid black" >Property Group Name </th>
                <th style="text-align:left ; border: 1px solid black">Property Summary</th>
            </tr>
            {% set pvgs = oc.applied_property_value_groups %}

               {% for pvg in pvgs %}
                <tr>
                    <td style="text-align:left ; border: 1px solid black">{{ pvg.name }}</td>
                    <td style="text-align:left ; border: 1px solid black">{{ pvg.summary }}</td>
                </tr>
                <tr>
                    <td style="text-align:right ; border: 1px solid black"> Properties of {{ pvg.name  }}</td>
                    <td style="text-align:left ; border: 1px solid black"> 
                            <table  style="border: 1px solid black; width:100% " >
                                <tr>
                                    <th style="text-align:left ;border: 1px solid black">Property Name  </th>
                                    <th style="text-align:left ; border: 1px solid black"> Property Value </th>
                                </tr>
                            {% for pvs in pvgs.property_values %}
                            <tr>
                                <td style="text-align:left ; border: 1px solid black">{{ pvs.name }} </td>
                                <td style="text-align:left ; border: 1px solid black">{{ filter_property_value(pvs.value)}}</td>
                            </tr>
                           {% endfor %}
                           </table>

                  </td>
                </tr>
               {% endfor %}

           </table>
         <p style="text-align: center;"><strong>Property Values Groups {{ oc.name }}</strong></p>
    {% else %}
        <!--<p style="text-align: left;">No extension applied property values groups.</p>-->
    {% endif %}
    """
    return templ

def Generate_Physical_Actors_Report( model ):
    templ = """
    <h1 style= "padding-left: 0" >Actor descritions</h1>
    {% for actor in model.pa.all_components.by_is_actor(True) %}
        <h2>{{ actor.name }} - <span style="font-size: 10px" > UUID: {{ actor.uuid }} </span> </h2>
        <p>{{ actor.description }}</p>
        {% if actor.applied_property_values %}
            <p  >The table below identifies property values of {{ node.name }}.</p>
                <table  style="border: 2px solid black; width:100% " >
                    <tr>
                        <th style="text-align:left ;border: 1px solid black" >Property Name </th>
                        <th style="text-align:left ; border: 1px solid black">Property Value</th>
                    </tr>
                   {% for pv in node.applied_property_values %}
                    <tr>
                        <td style="text-align:left ; border: 1px solid black">{{ pv.name }}</td>
                        <td style="text-align:left ; border: 1px solid black">{{ pv.value }}</td>
                    </tr>
                  {% endfor %}
                   </table>
                 <p style="text-align: center;"><strong>Property Values of {{ actor.name }}</strong></p>
            {% else %}
                <p style="text-align: left;">No property values were identified for{{ actor.name }}</p>
            {% endif %}   
            {% if actor.property_value_groups %}
            <p  >The table below identifies property values groups of {{ actor.name }}.</p>
                <table  style="border: 2px solid black; width:100% " >
                    <tr>
                        <th style="text-align:left ;border: 1px solid black" >Property Group Name </th>
                        <th style="text-align:left ; border: 1px solid black">Property Summary</th>
                    </tr>
                    {% set pvgs = node %}
                       {% for pvgs in pvgs.applied_property_value_groups %}
                        <tr>
                            <td style="text-align:left ; border: 1px solid black">{{ pvgs.name }}</td>
                            <td style="text-align:left ; border: 1px solid black">{{ pvgs.summary }}</td>
                        </tr>
                        <tr>
                            <td style="text-align:right ; border: 1px solid black"> Properties of {{ pvgs.name  }}</td>
                            <td style="text-align:left ; border: 1px solid black"> 
                                    <table  style="border: 1px solid black; width:100% " >
                                        <tr>
                                            <th style="text-align:left ;border: 1px solid black">Property Name  </th>
                                            <th style="text-align:left ; border: 1px solid black"> Property Value </th>
                                        </tr>
                                    {% for pvs in pvgs.property_values %}
                                    <tr>
                                        <td style="text-align:left ; border: 1px solid black">{{ pvs.name }} </td>
                                        <td style="text-align:left ; border: 1px solid black">{{ pvs.value }}</td>
                                    </tr>
                                   {% endfor %}
                                   </table>
                          </td>
                        </tr>
                       {% endfor %}
                   </table>
                 <p style="text-align: center;"><strong>Property Values Groups of {{ actor.name }}</strong></p>
            {% else %}
                <p style="text-align: left;">No property values groups were identified for of {{actor.name }}</p>
            {% endif %}
        <h3> {{ actor.name }} Ports </h3>
        {% for port in actor.physical_ports %}
            <p>{{ port.name }} - <span style="font-size: 10px" > UUID: {{ port.uuid }} </span>  </p>
            <p>{{ port.description }} </p>
            {% if port.property_values %}
            <p  >The table below identifies property values of {{ port.name }}.</p>
                <table  style="border: 2px solid black; width:100% " >
                    <tr>
                        <th style="text-align:left; border: 1px solid black" >Port </th>
                        <th style="text-align:left ;border: 1px solid black" >Property Name </th>
                        <th style="text-align:left ; border: 1px solid black">Property Value</th>
                    </tr>
                   {% for pv in port.property_values %}
                    <tr>
                        <td style="text-align:left ; border: 1px solid black" >
                            <p>{{ port.uuid }}</p>
                            <p>{{ port.name }}</p>
                        </td>
                        <td style="text-align:left ; border: 1px solid black">{{ pv.name }}</td>
                        <td style="text-align:left ; border: 1px solid black">{{ pv.value }}</td>
                    </tr>
                  {% endfor %}
                   </table>
                <p style="text-align: center;"><strong>Property Values of {{ port.name }}</strong></p>
            {% else %}
                <p style="text-align: left;">No property values were identified for {{ port.name }}</p>
            {% endif %}
            {% if port.links %}
             <p  >The table below identifies Physical Links of {{ port.name }}.</p>
             <table  style="border: 2px solid black; width:100% " >
                <tr>
                    <th style="text-align:left ;border: 1px solid black" >Link Name </th>
                    <th style="text-align:left ; border: 1px solid black">Link uuid</th>
                </tr>
                {% for l in port.links %}
                    <tr>
                        <td style="text-align:left ; border: 1px solid black">{{ l.name }}</td>
                        <td style="text-align:left ; border: 1px solid black">{{ l.uuid }}</td>
                    </tr>
                {% endfor %}
                </table>
                    <p style="text-align: center;"><strong> Physical Port Links = {{ port.name }}</strong></p>
            {% else %}
                <p style="text-align: left;">No allocated component ports found for Physical Lins {{ port.name }}</p>
            {% endif %}
             {% if port.PortAllocation %}
             <p  >The table below identifies Physical Links of {{ port.name }}.</p>
             <table  style="border: 2px solid black; width:100% " >
                <tr>
                    <th style="text-align:left ;border: 1px solid black" >Link Name </th>
                    <th style="text-align:left ; border: 1px solid black">Link uuid</th>
                </tr>
                {% for l in port.PortAllocatio %}
                    <tr>
                        <td style="text-align:left ; border: 1px solid black">{{ l.name }}</td>
                        <td style="text-align:left ; border: 1px solid black">{{ l.uuid }}</td>
                    </tr>
                {% endfor %}
                </table>
                    <p style="text-align: center;"><strong> Physical Links of {{ port.name }}</strong></p>
            {% else %}
                <p style="text-align: left;">No allocated component ports links found for {{ port.name }}</p>
            {% endif %}
        {% endfor %}
    {% endfor %}
    """
    return templ
def Generate_Logical_Actors_Report( model ):
    templ = """
    <h1 style= "padding-left: 0" >Actor descritions</h1>
    {% for actor in model.la.all_components.by_is_actor(True) %}
        <h2>{{ actor.name }} - <span style="font-size: 10px" > UUID: {{ actor.uuid }} </span> </h2>
        <p>{{ actor.description }}</p>
        {% if actor.applied_property_values %}
            <p  >The table below identifies property values of {{ node.name }}.</p>
                <table  style="border: 2px solid black; width:100% " >
                    <tr>
                        <th style="text-align:left ;border: 1px solid black" >Property Name </th>
                        <th style="text-align:left ; border: 1px solid black">Property Value</th>
                    </tr>
                   {% for pv in node.applied_property_values %}
                    <tr>
                        <td style="text-align:left ; border: 1px solid black">{{ pv.name }}</td>
                        <td style="text-align:left ; border: 1px solid black">{{ pv.value }}</td>
                    </tr>
                  {% endfor %}
                   </table>
                 <p style="text-align: center;"><strong>Property Values of {{ actor.name }}</strong></p>
            {% else %}
                <p style="text-align: left;">No property values were identified for{{ actor.name }}</p>
            {% endif %}   
            {% if actor.property_value_groups %}
            <p  >The table below identifies property values groups of {{ actor.name }}.</p>
                <table  style="border: 2px solid black; width:100% " >
                    <tr>
                        <th style="text-align:left ;border: 1px solid black" >Property Group Name </th>
                        <th style="text-align:left ; border: 1px solid black">Property Summary</th>
                    </tr>
                    {% set pvgs = node %}
                       {% for pvgs in pvgs.applied_property_value_groups %}
                        <tr>
                            <td style="text-align:left ; border: 1px solid black">{{ pvgs.name }}</td>
                            <td style="text-align:left ; border: 1px solid black">{{ pvgs.summary }}</td>
                        </tr>
                        <tr>
                            <td style="text-align:right ; border: 1px solid black"> Properties of {{ pvgs.name  }}</td>
                            <td style="text-align:left ; border: 1px solid black"> 
                                    <table  style="border: 1px solid black; width:100% " >
                                        <tr>
                                            <th style="text-align:left ;border: 1px solid black">Property Name  </th>
                                            <th style="text-align:left ; border: 1px solid black"> Property Value </th>
                                        </tr>
                                    {% for pvs in pvgs.property_values %}
                                    <tr>
                                        <td style="text-align:left ; border: 1px solid black">{{ pvs.name }} </td>
                                        <td style="text-align:left ; border: 1px solid black">{{ filter_property_value(pvs.value) }}</td>
                                    </tr>
                                   {% endfor %}
                                   </table>
                          </td>
                        </tr>
                       {% endfor %}
                   </table>
                 <p style="text-align: center;"><strong>Property Values Groups of {{ actor.name }}</strong></p>
            {% else %}
                <p style="text-align: left;">No property values groups were identified for of {{actor.name }}</p>
            {% endif %}
        <h3> {{ actor.name }} Ports </h3>
        {% for port in actor.logical_ports %}
            <p>{{ port.name }} - <span style="font-size: 10px" > UUID: {{ port.uuid }} </span>  </p>
            <p>{{ port.description }} </p>
            {% if port.property_values %}
            <p  >The table below identifies property values of {{ port.name }}.</p>
                <table  style="border: 2px solid black; width:100% " >
                    <tr>
                        <th style="text-align:left; border: 1px solid black" >Port </th>
                        <th style="text-align:left ;border: 1px solid black" >Property Name </th>
                        <th style="text-align:left ; border: 1px solid black">Property Value</th>
                    </tr>
                   {% for pv in port.property_values %}
                    <tr>
                        <td style="text-align:left ; border: 1px solid black" >
                            <p>{{ port.uuid }}</p>
                            <p>{{ port.name }}</p>
                        </td>
                        <td style="text-align:left ; border: 1px solid black">{{ pv.name }}</td>
                        <td style="text-align:left ; border: 1px solid black">{{ pv.value }}</td>
                    </tr>
                  {% endfor %}
                   </table>
                <p style="text-align: center;"><strong>Property Values of {{ port.name }}</strong></p>
            {% else %}
                <p style="text-align: left;">No property values were identified for {{ port.name }}</p>
            {% endif %}
            {% if port.links %}
             <p  >The table below identifies Physical Links of {{ port.name }}.</p>
             <table  style="border: 2px solid black; width:100% " >
                <tr>
                    <th style="text-align:left ;border: 1px solid black" >Link Name </th>
                    <th style="text-align:left ; border: 1px solid black">Link uuid</th>
                </tr>
                {% for l in port.links %}
                    <tr>
                        <td style="text-align:left ; border: 1px solid black">{{ l.name }}</td>
                        <td style="text-align:left ; border: 1px solid black">{{ l.uuid }}</td>
                    </tr>
                {% endfor %}
                </table>
                    <p style="text-align: center;"><strong> Physical Port Links = {{ port.name }}</strong></p>
            {% else %}
                <p style="text-align: left;">No allocated component ports found for Physical Lins {{ port.name }}</p>
            {% endif %}
             {% if port.PortAllocation %}
             <p  >The table below identifies Physical Links of {{ port.name }}.</p>
             <table  style="border: 2px solid black; width:100% " >
                <tr>
                    <th style="text-align:left ;border: 1px solid black" >Link Name </th>
                    <th style="text-align:left ; border: 1px solid black">Link uuid</th>
                </tr>
                {% for l in port.PortAllocatio %}
                    <tr>
                        <td style="text-align:left ; border: 1px solid black">{{ l.name }}</td>
                        <td style="text-align:left ; border: 1px solid black">{{ l.uuid }}</td>
                    </tr>
                {% endfor %}
                </table>
                    <p style="text-align: center;"><strong> Physical Links of {{ port.name }}</strong></p>
            {% else %}
                <p style="text-align: left;">No allocated component ports links found for {{ port.name }}</p>
            {% endif %}
        {% endfor %}
    {% endfor %}
    """
    return templ

def Generate_Physical_Node_Components_Report( model ):
    templ = """

    <h1 style= "padding-left: 0" >Node descriptions</h1>
    {% for node in model.pa.all_components %}
        <h2>{{ node.name }} - <span style="font-size: 10px" > UUID: {{ node.uuid }} </span> </h2>
        <p>{{ node.description }}</p>
         {% if node.applied_property_values %}
            <p  >The table below identifies property values of {{ node.name }}.</p>
                <table  style="border: 2px solid black; width:100% " >
                    <tr>
                        <th style="text-align:left ;border: 1px solid black" >Property Name </th>
                        <th style="text-align:left ; border: 1px solid black">Property Value</th>
                    </tr>
                   {% for pv in node.applied_property_values %}
                    <tr>
                        <td style="text-align:left ; border: 1px solid black">{{ pv.name }}</td>
                        <td style="text-align:left ; border: 1px solid black">{{ pv.value }}</td>
                    </tr>
                  {% endfor %}
                   </table>
                 <p style="text-align: center;"><strong>Property Values of {{ node.name }}</strong></p>
            {% else %}
                <p style="text-align: left;">No property values were identified.</p>
            {% endif %}   
            {% if node.property_value_groups %}
            <p  >The table below identifies property values groups of {{ node.name }}.</p>
                <table  style="border: 2px solid black; width:100% " >
                    <tr>
                        <th style="text-align:left ;border: 1px solid black" >Property Group Name </th>
                        <th style="text-align:left ; border: 1px solid black">Property Summary</th>
                    </tr>
                    {% set pvgs = node %}

                       {% for pvgs in pvgs.applied_property_value_groups %}
                        <tr>
                            <td style="text-align:left ; border: 1px solid black">{{ pvgs.name }}</td>
                            <td style="text-align:left ; border: 1px solid black">{{ pvgs.summary }}</td>
                        </tr>
                        <tr>
                            <td style="text-align:right ; border: 1px solid black"> Properties of {{ pvgs.name  }}</td>
                            <td style="text-align:left ; border: 1px solid black"> 
                                    <table  style="border: 1px solid black; width:100% " >
                                        <tr>
                                            <th style="text-align:left ;border: 1px solid black">Property Name  </th>
                                            <th style="text-align:left ; border: 1px solid black"> Property Value </th>
                                        </tr>
                                    {% for pvs in pvgs.property_values %}
                                    <tr>
                                        <td style="text-align:left ; border: 1px solid black">{{ pvs.name }} </td>
                                        <td style="text-align:left ; border: 1px solid black">{{ pvs.value }}</td>
                                    </tr>
                                   {% endfor %}
                                   </table>

                          </td>
                        </tr>
                       {% endfor %}

                   </table>
                 <p style="text-align: center;"><strong>Property Values Groups {{ node.name }}</strong></p>
            {% else %}
                <p style="text-align: left;">No property values groups were identified.</p>
            {% endif %}
        <h3> {{ node.name }} Ports </h3>
        {% for port in node.physical_ports %}
            <p>{{ port.name }} - <span style="font-size: 10px" > UUID: {{ port.uuid }} </span>  </p>
            <p>{{ port.description }} </p>
            {% if port.property_values %}
            <p  >The table below identifies property values of {{ port.name }}.</p>
                <table  style="border: 2px solid black; width:100% " >
                    <tr>
                        <th style="text-align:left; border: 1px solid black" >Port </th>
                        <th style="text-align:left ;border: 1px solid black" >Property Name </th>
                        <th style="text-align:left ; border: 1px solid black">Property Value</th>
                    </tr>
                   {% for pv in port.property_values %}
                    <tr>
                        <td style="text-align:left ; border: 1px solid black" >
                            <p>{{ port.uuid }}</p>
                            <p>{{ port.name }}</p>
                        </td>
                        <td style="text-align:left ; border: 1px solid black">{{ pv.name }}</td>
                        <td style="text-align:left ; border: 1px solid black">{{ pv.value }}</td>
                    </tr>
                  {% endfor %}
                   </table>
                <p style="text-align: center;"><strong>Property Values of {{ port.name }}</strong></p>
            {% else %}
                <p style="text-align: left;">No property values were identified.</p>
            {% endif %}
            {% if port.links %}
             <p  >The table below identifies Physical Links of {{ port.name }}.</p>
             <table  style="border: 2px solid black; width:100% " >
                <tr>
                    <th style="text-align:left ;border: 1px solid black" >Link Name </th>
                    <th style="text-align:left ; border: 1px solid black">Link uuid</th>
                </tr>

                {% for l in port.links %}
                    <tr>
                        <td style="text-align:left ; border: 1px solid black">{{ l.name }}</td>
                        <td style="text-align:left ; border: 1px solid black">{{ l.uuid }}</td>
                    </tr>
                {% endfor %}
                </table>
                    <p style="text-align: center;"><strong> Physical Links = {{ port.name }}</strong></p>
            {% else %}
                <p style="text-align: left;">No allocated component ports found.</p>
            {% endif %}
             {% if port.PortAllocation %}
             <p  >The table below identifies Physical Links of {{ port.name }}.</p>
             <table  style="border: 2px solid black; width:100% " >
                <tr>
                    <th style="text-align:left ;border: 1px solid black" >Link Name </th>
                    <th style="text-align:left ; border: 1px solid black">Link uuid</th>
                </tr>

                {% for l in port.PortAllocatio %}
                    <tr>
                        <td style="text-align:left ; border: 1px solid black">{{ l.name }}</td>
                        <td style="text-align:left ; border: 1px solid black">{{ l.uuid }}</td>
                    </tr>
                {% endfor %}
                </table>
                    <p style="text-align: center;"><strong> Physical Links = {{ port.name }}</strong></p>
            {% else %}
                <p style="text-align: left;">No allocated component ports found.</p>
            {% endif %}
        {% endfor %}
    {% endfor %}
    """
    return templ

def Display_Component_Report( pc ):
   
    template = """
    <h1>{{ node.name }} - <span style="font-size: 10px" > UUID: {{ node.uuid }} </span> </h2>
    <p>{{ node.description }}</p> 
    {% if node.applied_property_values %}
    <p  >The table below identifies property values of {{ node.name }}.</p>
        <table  style="border: 2px solid black; width:100% " >
            <tr>
                <th style="text-align:left ;border: 1px solid black" >Property Name </th>
                <th style="text-align:left ; border: 1px solid black">Property Value</th>
            </tr>
           {% for pv in node.applied_property_values %}
            <tr>
                <td style="text-align:left ; border: 1px solid black">{{ pv.name }}</td>
                <td style="text-align:left ; border: 1px solid black">{{ pv.value }}</td>
            </tr>
          {% endfor %}
           </table>
         <p style="text-align: center;"><strong>Property Values of {{ node.name }}</strong></p>
    {% else %}
        <p style="text-align: left;">No property values were identified.</p>
    {% endif %}   
    {% if node.applied_property_value_groups %}
    <p  >The table below identifies property values groups of {{ node.name }}.</p>
        <table  style="border: 2px solid black; width:100% " >
            <tr>
                <th style="text-align:left ;border: 1px solid black" >Property Group Name </th>
                <th style="text-align:left ; border: 1px solid black">Property Summary</th>
            </tr>
            {% set pvgs = node %}
    
               {% for pvgs in pvgs.applied_property_value_groups %}
                <tr>
                    <td style="text-align:left ; border: 1px solid black">{{ pvgs.name }}</td>
                    <td style="text-align:left ; border: 1px solid black">{{ pvgs.summary }}</td>
                </tr>
                <tr>
                    <td style="text-align:right ; border: 1px solid black"> Properties of {{ pvgs.name  }}</td>
                    <td style="text-align:left ; border: 1px solid black"> 
                            <table  style="border: 1px solid black; width:100% " >
                                <tr>
                                    <th style="text-align:left ;border: 1px solid black">Property Name  </th>
                                    <th style="text-align:left ; border: 1px solid black"> Property Value </th>
                                </tr>
                            {% for pvs in pvgs.property_values %}
                            <tr>
                                <td style="text-align:left ; border: 1px solid black">{{ pvs.name }} </td>
                                <td style="text-align:left ; border: 1px solid black">{{ filter_property_value(pvs.value) }}</td>
                            </tr>
                           {% endfor %}
                           </table>
    
                  </td>
                </tr>
               {% endfor %}
    
           </table>
         <p style="text-align: center;"><strong>Property Values Groups {{ node.name }}</strong></p>
    {% else %}
        <p style="text-align: left;">No appllied property value groups were identified.</p>
    {% endif %}
    <h3> {{ node.name }} Ports </h3>
    {% for port in node.ports %}
        <p>{{ port.name }} - <span style="font-size: 10px" > UUID: {{ port.uuid }} </span>  </p>
        <p>{{ port.description }} </p>
        {% if port.property_values %}
        <p  >The table below identifies property values of {{ port.name }}.</p>
            <table  style="border: 2px solid black; width:100% " >
                <tr>
                    <th style="text-align:left; border: 1px solid black" >Port </th>
                    <th style="text-align:left ;border: 1px solid black" >Property Name </th>
                    <th style="text-align:left ; border: 1px solid black">Property Value</th>
                </tr>
               {% for pv in port.property_values %}
                <tr>
                    <td style="text-align:left ; border: 1px solid black" >
                        <p>{{ port.uuid }}</p>
                        <p>{{ port.name }}</p>
                    </td>
                    <td style="text-align:left ; border: 1px solid black">{{ pv.name }}</td>
                    <td style="text-align:left ; border: 1px solid black">{{ pv.value }}</td>
                </tr>
              {% endfor %}
               </table>
            <p style="text-align: center;"><strong>Property Values of {{ port.name }}</strong></p>
        {% else %}
           
        {% endif %}
        {% if port.exchanges %}
         <p  >The table below identifies Component Exchanges of {{ port.name }}.</p>
         <table  style="border: 2px solid black; width:100% " >
            <tr>
                <th style="text-align:left ;border: 1px solid black" >Exchange Name </th>
                <th style="text-align:left ; border: 1px solid black">Exchange uuid</th>
                <th style="text-align:left ; border: 1px solid black"> Name</th>
                <th style="text-align:left ; border: 1px solid black"> Owner Direction</th>
            </tr>

            {% for exs in port.exchanges %}
                <tr>
                    <td style="text-align:left ; border: 1px solid black">{{ exs.name }}</td>
                    <td style="text-align:left ; border: 1px solid black">{{ exs.uuid }}</td>
                    <td style="text-align:left ; border: 1px solid black">{{ exs.source.owner.name}}, {{ exs.source.direction }}</td>
                    <td style="text-align:left ; border: 1px solid black">{{ exs.target.owner.name}}, {{ exs.target.direction }}</td>
                    <p style="text-align: center;">Component Exchange: <strong> {{ exs.name }}</strong></p>
                    {% if exs.property_value_groups %}
                    <table  style="border: 2px solid black; width:100% " >
                        <tr>
                            <th style="text-align:left ;border: 1px solid black" >Property Group Name </th>
                            <th style="text-align:left ; border: 1px solid black">Property Summary</th>
                             {% set pvgs = exs %}
                                
                                {% for pvgs in pvgs.applied_property_value_groups %}
                                <tr>
                                    <td style="text-align:left ; border: 1px solid black">{{ pvgs.name }}</td>
                                    <td style="text-align:left ; border: 1px solid black">{{ pvgs.summary }}</td>
                                </tr>
                                <tr>
                                    <td style="text-align:right ; border: 1px solid black"> Properties of {{ pvgs.name  }}</td>
                                    <td style="text-align:left ; border: 1px solid black"> 
                                            <table  style="border: 1px solid black; width:100% " >
                                                <tr>
                                                    <th style="text-align:left ;border: 1px solid black">Property Name  </th>
                                                    <th style="text-align:left ; border: 1px solid black"> Property Value </th>
                                                </tr>
                                            {% for pvs in pvgs.property_values %}
                                            <tr>
                                                <td style="text-align:left ; border: 1px solid black">{{ pvs.name }} </td>
                                                <td style="text-align:left ; border: 1px solid black">{{ filter_property_value(pvs.value)}}</td>
                                            </tr>
                                           {% endfor %}
                                           </table>
                                </tr>
                                {% endfor %}
                                
                                </table>
                                
                                {% else %}
                                
                                {% endif %} 
                            
                        </tr>
                        
         
                </tr>
            {% endfor %}
            </table>
               
        {% else %}
            <p style="text-align: left;">No port eschanges found.</p>
        {% endif %}
       
    {% endfor %}
    """
    env = jinja2.Environment()
    #print(template)
    rendered_template = env.from_string(template).render(node=pc,  filter_property_value=filter_property_value)
    #print(rendered_template )
    display.display(HTML(rendered_template ))
    for func in pc.allocated_functions :
        Generate_Function_Report( func)
        env = jinja2.Environment()
        #print(template)
        rendered_template = env.from_string(Generate_Function_Report(func)).render(oa=func)
        #print(rendered_template )
        display.display(HTML(rendered_template ))
    

def Generate_Physical_Interfaces_Report( model ):
    templ = """

    <h1 style= "padding-left: 0" >Interfaces </h1>
    {% for node in model.pa.all_interfaces %}
        <h2>{{ node.name }} - <span style="font-size: 10px" > UUID: {{ node.uuid }} </span> </h2>
        <p>{{ node.description }}</p>
        <h3> {{ node.name }} Ports </h3>
        {% for port in node.physical_ports %}
            <p>{{ port.name }} - <span style="font-size: 10px" > UUID: {{ port.uuid }} </span>  </p>
            <p>{{ port.description }} </p>
            {% if port.property_values %}
            <p  >The table below identifies property values of {{ port.name }}.</p>
                <table  style="border: 2px solid black; width:100% " >
                    <tr>
                        <th style="text-align:left; border: 1px solid black" > Port </th>
                        <th style="text-align:left ;border: 1px solid black" >Property Name </th>
                        <th style="text-align:left ; border: 1px solid black">Property Value</th>
                    </tr>
                {% for pv in port.property_values %}

                    <tr>
                        <td style="text-align:left ; border: 1px solid black" >
                            <p>{{ port.uuid }}</p>
                            <p>{{ port.name }}</p>
                        </td>
                        <td style="text-align:left ; border: 1px solid black">{{ pv.name }}</td>
                        <td style="text-align:left ; border: 1px solid black">{{ pv.value }}</td>
                    </tr>
                {% endfor %}
                </table>
                    <p style="text-align: center;"><strong>Property Values of {{ port.name }}</strong></p>
            {% else %}
                <p style="text-align: left;">No property values were identified.</p>
            {% endif %}
        {% endfor %}
    {% endfor %}
    """
    return templ




def Display_Operational_Processes_Tables(fc):
    #print(fc)
    print()
    #print("Functional Chain:", fc.name)
    display.display(Markdown(f"# Functional Chain: {fc.name}"))
    
    
    df = pd.DataFrame({
    'Function Owner': [],
    'Function': [],
    'Function Exchange': [],
    'Function Exchange Items': [],
    'Function Exchange Item Elements': [],
    })
    def Append_Row_to_Dataframe(df,  Current_Function_Owner ,Current_Function,\
                               Current_Function_Exchange , Current_Function_Exchange_EI, Current_Function_Exchange_EIE) :
        df.loc[len(df)] = [Current_Function_Owner ,Current_Function,\
                                Current_Function_Exchange , Current_Function_Exchange_EI, Current_Function_Exchange_EIE]
        
    for function in fc.involved_functions:
        #This will initialize all the table elements
        #print(function)
        Current_Function_Owner = ''
        Current_Function =''
        Current_Function_Exchange = ''
        Current_Function_Exchange_EI = ''
        Current_Function_Exchange_EIE = ''
        
        #print(function.owner)
        if function.owner != None :
         
            Current_Function_Owner=function.owner.name
            #print("- Entity:",Current_Function_Owner)
            #print("-Function:",function.name)
            Current_Function = function.name
            #print("-Function:",Current_Function)
           
            
            #print("---Exch:",exchange.name)
            if function.outputs :
                for exchange in function.outputs:
                          
                    for involved_exchange in fc.involved_links:
                         if exchange == involved_exchange:
                             Current_Function_Exchange = exchange.name
                             #print("--Output:",output.name)
                             #print("---Exch:",Current_Function_Exchange)
                             
                             for exchange_item in exchange.exchange_items: 
                                 Current_Function_Exchange_EI = exchange_item.name
                                 #print("--Output:",output.name)
                                 #print(exchange_item)
                                 #print("---Exch Item:",Current_Function_Exchange_EI)
    
                                 for element in exchange_item.elements: 
                                     Current_Function_Exchange_EIE = element.name
                                     #print(element)
                                     #print("---Exch Item Elements:",Current_Function_Exchange_EIE)
                                     Append_Row_to_Dataframe(df,  Current_Function_Owner ,Current_Function,\
                                        Current_Function_Exchange , Current_Function_Exchange_EI, Current_Function_Exchange_EIE)
                                 if  exchange_item.elements ==  []:
                                     Append_Row_to_Dataframe(df,  Current_Function_Owner ,Current_Function,\
                                    Current_Function_Exchange , Current_Function_Exchange_EI, Current_Function_Exchange_EIE) 
                             if exchange.exchange_items == [] :
                                Append_Row_to_Dataframe(df,  Current_Function_Owner ,Current_Function,\
                                Current_Function_Exchange , Current_Function_Exchange_EI, Current_Function_Exchange_EIE) 
            else: 
                Append_Row_to_Dataframe(df,  Current_Function_Owner ,Current_Function,\
                                Current_Function_Exchange , Current_Function_Exchange_EI, Current_Function_Exchange_EIE)
           
        
        else: 
            Current_Function_Owner="None"
            print("-Entity","None")
            Current_Function = function.name
            print("-Function",Current_Function )
            if function.outputs :    
                for exchange in function.outputs:  
                    
                   for involved_exchange in fc.involved_links:
                         if exchange == involved_exchange:
                             
                             
                             Current_Function_Exchange = exchange.name
                             #print("--Output:",output.name)
                             #print("---Exch:",Current_Function_Exchange)
                             if exchange.exchange_items == [] :
                                 Append_Row_to_Dataframe(df,  Current_Function_Owner ,Current_Function,\
                                 Current_Function_Exchange , Current_Function_Exchange_EI, Current_Function_Exchange_EIE)   
                             for exchange_item in exchange.exchange_items: 
                                 Current_Function_Exchange_EI = exchange_item.name
                                 #print("--Output:",output.name)
                                 #print(exchange_item)
                                 #print("---Exch Item:",Current_Function_Exchange_EI)
                                 
                                 
                                 for element in exchange_item.elements: 
                                     Current_Function_Exchange_EIE = element.name
                                     #print(element)
                                     #print("---Exch Item Elements:",Current_Function_Exchange_EIE)
                                     Append_Row_to_Dataframe(df,  Current_Function_Owner ,Current_Function,\
                                       Current_Function_Exchange , Current_Function_Exchange_EI, Current_Function_Exchange_EIE)
                                 if exchange_item.elements == []:
                                     Append_Row_to_Dataframe(df,  Current_Function_Owner ,Current_Function,\
                                    Current_Function_Exchange , Current_Function_Exchange_EI, Current_Function_Exchange_EIE) 
                             if exchange.exchange_items == [] :
                                 Append_Row_to_Dataframe(df,  Current_Function_Owner ,Current_Function,\
                                 Current_Function_Exchange , Current_Function_Exchange_EI, Current_Function_Exchange_EIE)    
            else: 
                Append_Row_to_Dataframe(df,  Current_Function_Owner ,Current_Function,\
                                Current_Function_Exchange , Current_Function_Exchange_EI, Current_Function_Exchange_EIE)
           
                               
                                          
       
    
    
    display.display(df)


def Display_Operational_Process_Report(fc):
    #print(fc)
    
    env = jinja2.Environment()
    display.display(HTML(env.from_string(Generate_Operational_Process_Report(fc)).render(op=fc,  filter_property_value=filter_property_value)))
    print()
    #print("Functional Chain:", fc.name)
    display.display(Markdown(f"Operational Process: {fc.name}"))
    
    
    df = pd.DataFrame({
    'Activity Owner': [],
    'Activity': [],
    'Interaction': [],
    'Exchange Items': [],
    'Exchange Item Elements': [],
    })
    def Append_Row_to_Dataframe(df,  Current_Function_Owner ,Current_Function,\
                               Current_Function_Exchange , Current_Function_Exchange_EI, Current_Function_Exchange_EIE) :
        df.loc[len(df)] = [Current_Function_Owner ,Current_Function,\
                                Current_Function_Exchange , Current_Function_Exchange_EI, Current_Function_Exchange_EIE]
        
    for function in fc.involved_functions:
        #This will initialize all the table elements
        #print(function)
        Current_Function_Owner = ''
        Current_Function =''
        Current_Function_Exchange = ''
        Current_Function_Exchange_EI = ''
        Current_Function_Exchange_EIE = ''
        
        #print(function.owner)
        if function.owner != None :
         
            Current_Function_Owner=function.owner.name
            #print("- Entity:",Current_Function_Owner)
            #print("-Function:",function.name)
            Current_Function = function.name
            #print("-Function:",Current_Function)
           
            
            #print("---Exch:",exchange.name)
            if function.outputs :
                for exchange in function.outputs:
                    #print(exchange)      
                    for involved_exchange in fc.involved_links:
                         if exchange == involved_exchange:
                             Current_Function_Exchange = exchange.name
                             #print("--Output:",output.name)
                             #print("---Exch:",Current_Function_Exchange)
                             
                             for exchange_item in exchange.exchange_items: 
                                 Current_Function_Exchange_EI = exchange_item.name
                                 #print("--Output:",output.name)
                                 #print(exchange_item)
                                 #print("---Exch Item:",Current_Function_Exchange_EI)
    
                                 for element in exchange_item.elements: 
                                     Current_Function_Exchange_EIE = element.name
                                     #print(element)
                                     #print("---Exch Item Elements:",Current_Function_Exchange_EIE)
                                     Append_Row_to_Dataframe(df,  Current_Function_Owner ,Current_Function,\
                                        Current_Function_Exchange , Current_Function_Exchange_EI, Current_Function_Exchange_EIE)
                                 if  exchange_item.elements ==  []:
                                     Append_Row_to_Dataframe(df,  Current_Function_Owner ,Current_Function,\
                                    Current_Function_Exchange , Current_Function_Exchange_EI, Current_Function_Exchange_EIE) 
                             if exchange.exchange_items == [] :
                                Append_Row_to_Dataframe(df,  Current_Function_Owner ,Current_Function,\
                                Current_Function_Exchange , Current_Function_Exchange_EI, Current_Function_Exchange_EIE) 
            else: 
                Append_Row_to_Dataframe(df,  Current_Function_Owner ,Current_Function,\
                                Current_Function_Exchange , Current_Function_Exchange_EI, Current_Function_Exchange_EIE)
          
        else: 
            Current_Function_Owner="None"
            print("-Entity","None")
            Current_Function = function.name
            print("-Function",Current_Function )
            if function.outputs :
                for exchange in function.outputs:  
                    
                   for involved_exchange in fc.involved_links:
                         if exchange == involved_exchange:
                             
                             
                             Current_Function_Exchange = exchange.name
                             #print("--Output:",output.name)
                             #print("---Exch:",Current_Function_Exchange)
                             if exchange.exchange_items == [] :
                                 Append_Row_to_Dataframe(df,  Current_Function_Owner ,Current_Function,\
                                 Current_Function_Exchange , Current_Function_Exchange_EI, Current_Function_Exchange_EIE)   
                             for exchange_item in exchange.exchange_items: 
                                 Current_Function_Exchange_EI = exchange_item.name
                                 #print("--Output:",output.name)
                                 #print(exchange_item)
                                 #print("---Exch Item:",Current_Function_Exchange_EI)
                                 
                                 
                                 for element in exchange_item.elements: 
                                     Current_Function_Exchange_EIE = element.name
                                     #print(element)
                                     #print("---Exch Item Elements:",Current_Function_Exchange_EIE)
                                     Append_Row_to_Dataframe(df,  Current_Function_Owner ,Current_Function,\
                                       Current_Function_Exchange , Current_Function_Exchange_EI, Current_Function_Exchange_EIE)
                                 if exchange_item.elements == []:
                                     Append_Row_to_Dataframe(df,  Current_Function_Owner ,Current_Function,\
                                    Current_Function_Exchange , Current_Function_Exchange_EI, Current_Function_Exchange_EIE) 
                             if exchange.exchange_items == [] :
                                 Append_Row_to_Dataframe(df,  Current_Function_Owner ,Current_Function,\
                                 Current_Function_Exchange , Current_Function_Exchange_EI, Current_Function_Exchange_EIE)    
                                   
                if  function.outputs == []:
                    Append_Row_to_Dataframe(df,  Current_Function_Owner ,Current_Function,\
                         Current_Function_Exchange , Current_Function_Exchange_EI, Current_Function_Exchange_EIE)                                 
            else: 
                Append_Row_to_Dataframe(df,  Current_Function_Owner ,Current_Function,\
                                Current_Function_Exchange , Current_Function_Exchange_EI, Current_Function_Exchange_EIE)
            
    display.display(df)
    display.display(Markdown(f"# Operational Activites"))
    functions = fc.involved_functions
    sorted_functions = sorted(functions, key=lambda function: function.name)
                               
    for function in sorted_functions:
        display.display(HTML(env.from_string(Generate_Operational_Activity_Report(function)).render(oa=function ,  filter_property_value=filter_property_value)))
        #display.display(HTML(env.from_string(Generate_Operational_Process_Report(fc)).render(op=fc)))   

def Display_Functional_Chain_Report(fc):
    #print(fc)
    
    env = jinja2.Environment()
    display.display(HTML(env.from_string(Generate_Functional_Chain_Report(fc)).render(op=fc,  filter_property_value=filter_property_value)))
    print()
    #print("Functional Chain:", fc.name)
    display.display(Markdown(f"Functional_Chain: {fc.name}"))
    
    df = pd.DataFrame({
    'Function Owner': [],
    'Function': [],
    'Function Exchange': [],
    'Function Exchange Items': [],
    'Function Exchange Item Elements': [],
    })
    def Append_Row_to_Dataframe(df,  Current_Function_Owner ,Current_Function,\
                               Current_Function_Exchange , Current_Function_Exchange_EI, Current_Function_Exchange_EIE) :
        print("appending")
        df.loc[len(df)] = [Current_Function_Owner ,Current_Function,\
                                Current_Function_Exchange , Current_Function_Exchange_EI, Current_Function_Exchange_EIE]
        
    for function in fc.involved_functions:
        #This will initialize all the table elements
        Current_Function_Owner = ''
        Current_Function =''
        Current_Function_Exchange = ''
        Current_Function_Exchange_EI = ''
        Current_Function_Exchange_EIE = ''
        
        #print(function.owner)
        if function.owner != None :
         
            Current_Function_Owner=function.owner.name
            print("- Entity:",Current_Function_Owner)
            print("-Function:",function.name)
            Current_Function = function.name
            print("-Function:",Current_Function)

            for output in function.outputs:
                #print(output)
                is_FOs= True
                Current_Function_OPort = output.name
                Append_Row_to_Dataframe(df,  Current_Function_Owner ,Current_Function,\
                                 Current_Function_Exchange , Current_Function_Exchange_EI, Current_Function_Exchange_EIE)
                for exchange in output.exchanges:         
                    for involved_exchange in fc.involved_links:
                         if exchange == involved_exchange:
                             Current_Function_Exchange = exchange.name
                             print("--Output:",output.name)
                             print("---Exch:",Current_Function_Exchange)
                             
                             for exchange_item in exchange.exchange_items: 
                                 Current_Function_Exchange_EI = exchange_item.name
                                 print("--Output:",output.name)
                                 #print(exchange_item)
                                 print("---Exch Item:",Current_Function_Exchange_EI)

                                 for element in exchange_item.elements: 
                                     Current_Function_Exchange_EIE = element.name
                                     #print(element)
                                     print("---Exch Item Elements:",Current_Function_Exchange_EIE)
                                     Append_Row_to_Dataframe(df,  Current_Function_Owner ,Current_Function,\
                                        Current_Function_Exchange , Current_Function_Exchange_EI, Current_Function_Exchange_EIE)
                                 if  exchange_item.elements ==  []:
                                     Append_Row_to_Dataframe(df,  Current_Function_Owner ,Current_Function,\
                                    Current_Function_Exchange , Current_Function_Exchange_EI, Current_Function_Exchange_EIE) 
                             if exchange.exchange_items == [] :
                                Append_Row_to_Dataframe(df,  Current_Function_Owner ,Current_Function,\
                                Current_Function_Exchange , Current_Function_Exchange_EI, Current_Function_Exchange_EIE) 
          
        else: 
            Current_Function_Owner="None"
            print("-Entity","None")
            Current_Function = function.name
            print("-Function",Current_Function )

            for output in function.outputs:  
                Current_Function_OPort = output.name
                Current_Function_OPort = output.name
                Append_Row_to_Dataframe(df,  Current_Function_Owner ,Current_Function,\
                    Current_Function_Exchange , Current_Function_Exchange_EI, Current_Function_Exchange_EIE)
                for exchange in output.exchanges:
                   for involved_exchange in fc.involved_links:
                         if exchange == involved_exchange:
                             
                             
                             Current_Function_Exchange = exchange.name
                             #print("--Output:",output.name)
                             #print("---Exch:",Current_Function_Exchange)
                             if exchange.exchange_items == [] :
                                 Append_Row_to_Dataframe(df,  Current_Function_Owner ,Current_Function,\
                                 Current_Function_Exchange , Current_Function_Exchange_EI, Current_Function_Exchange_EIE)   
                             for exchange_item in exchange.exchange_items: 
                                 Current_Function_Exchange_EI = exchange_item.name
                                 #print("--Output:",output.name)
                                 #print(exchange_item)
                                 #print("---Exch Item:",Current_Function_Exchange_EI)
                                 
                                 
                                 for element in exchange_item.elements: 
                                     Current_Function_Exchange_EIE = element.name
                                     #print(element)
                                     #print("---Exch Item Elements:",Current_Function_Exchange_EIE)
                                     Append_Row_to_Dataframe(df,  Current_Function_Owner ,Current_Function,\
                                       Current_Function_Exchange , Current_Function_Exchange_EI, Current_Function_Exchange_EIE)
                                 if exchange_item.elements == []:
                                     Append_Row_to_Dataframe(df,  Current_Function_Owner ,Current_Function,\
                                    Current_Function_Exchange , Current_Function_Exchange_EI, Current_Function_Exchange_EIE) 
                             if exchange.exchange_items == [] :
                                 Append_Row_to_Dataframe(df,  Current_Function_Owner ,Current_Function,\
                                 Current_Function_Exchange , Current_Function_Exchange_EI, Current_Function_Exchange_EIE)    
                               
            if  function.outputs == []:
                Append_Row_to_Dataframe(df,  Current_Function_Owner ,Current_Function,\
                     Current_Function_Exchange , Current_Function_Exchange_EI, Current_Function_Exchange_EIE)                                 

    display.display(df)
    display.display(Markdown(f"# Functional Chain"))
    functions = fc.involved_functions
    sorted_functions = sorted(functions, key=lambda function: function.name)
                               
    for function in sorted_functions:
        display.display(HTML(env.from_string(Generate_Function_Report(function)).render(oa=function,  filter_property_value=filter_property_value)))
        #display.display(HTML(env.from_string(Generate_Operational_Process_Report(fc)).render(op=fc)))   