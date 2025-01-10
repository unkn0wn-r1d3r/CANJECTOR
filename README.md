<h1 align="center">CANJECTOR</h1>


```diff
- Warning: Educational Use Only

-This program is intended solely for educational purposes. Under no circumstances should this program be used to cause harm or damage to any systems, data, or individuals. The creator of this program disclaims any responsibility for damages or ---consequences resulting from the use or misuse of this software.
```

![downloadfile-8](https://github.com/user-attachments/assets/4607b442-c341-4673-a63a-7885bc883d4e)


<p>CANJECTOR is a Can Bus Pentesting tool which can be used to monitor and inject the CAN BUS packet of vechicle.</p>

<h2>CANJECTOR have two part</h2>
<ol>
  <li>CANJECTOR Application : Developed using python and pyside6.This Application is processing the data and analyze it and inject the payloads.</li>
  <li>Arduino Nano + MCP2515 Module + OBD2 Connector : This hardware will connect to OBD2 Port on the vechicle and read CAN BUS packet. </li>
  
</ol>  
<h2>Features</h2>
 <ol type="1">
  <li>Show Repeative Packets</li>
  <li>Unchanged Packet detection</li>
   <li>Search Option</li>
   <li>Fuzzing Attack</li>
   <li>Replay Attack</li>
   <li>Inject ID</li>
   <li>Inject Data</li>
   <li>CAN Packet Save</li>
  </ol> 

  <h3>DIY Hardware</h3>
      <h4>Features</h4>
   <ol type="1">
    <li>Arduino Nano</li>
    <li>MCP2515</li>
    </ol> 
<h3>Connection Diagram From Arduino Nano To MCP2515 Module</h3>

<table style="width:100%">
  <tr>
    <th>Arduino Nano</th>
    <th>MCP2515 Module</th>
      </tr>
  <tr>
    <td>5V</td>
    <td>VCC</td>
    
  </tr>
  <tr>
    <td>GND</td>
    <td>GND</td>
    
  </tr>
   <tr>
    <td>D10</td>
    <td>CS</td>
      </tr>
      <tr>
    <td>D11</td>
    <td>(MOSI)SI</td>
      </tr>
            <tr>
    <td>D12</td>
    <td>(MISO)SO</td>
      </tr>
            <tr>
    <td>D13</td>
    <td>(SCK)SCK</td>
      </tr>
      <tr>
    <td>D2</td>
    <td>INT (optional, for interrupt-driven operation)</td>
      </tr>
</table>

<h3>Connection Diagram From MCP2515 Module To OBD2 Connector</h3>

<table style="width:100%">
  <tr>
    <th>MCP2515 Module</th>
    <th>OBD2 Connector</th>
      </tr>
  <tr>
    <td>CANH (CAN High) </td>
    <td>Pin 6 (CAN High)</td>
    
  </tr>
  <tr>
    <td>CANL (CAN Low)</td>
    <td>Pin 14 (CAN Low)</td>
    
  </tr>
  </table>
  <h2>CANJECTOR Application</h2>
  
![image](https://github.com/user-attachments/assets/76b95084-7371-4387-8270-ebe495762f5e)

