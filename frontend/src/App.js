import logo from './logo.svg';
import './App.css';

import React, { useState, useEffect, useRef } from 'react';
import { DataTable } from 'primereact/datatable';
import { Column } from 'primereact/column';
import { Panel } from 'primereact/panel';
import { Button } from 'primereact/button';
import 'primereact/resources/themes/saga-blue/theme.css'; //theme
import 'primereact/resources/primereact.min.css'; //core css
import 'primeicons/primeicons.css'; //icons

import Message from './Message.js'
import messages from './removableResults.json';
console.log(messages);


function App() {
  const [expandedRows, setExpandedRows] = useState(null);

  const rowExpansionTemplate = (data) => {
    return (
      <div className="expanded">
        <Panel header={data.Subject}>
          <p className='snippet'>
            {data.snippet}
          </p>
        </Panel>
      </div>
    )
  }

  const openMessageTemplate = (rowData) => {
    return (
      <div className="openMessage">
        <Button
          label="Open"
          onClick={() => window.open(rowData.url, "_blank")}
        />
      </div>
    )
  }

  return (
    <div className="App">
      <header className="App-header">
        <img src={logo} className="App-logo" alt="logo" />
        <p>
          Edit <code>src/App.js</code> and save to reload.
        </p>
        <a
          className="App-link"
          href="https://reactjs.org"
          target="_blank"
          rel="noopener noreferrer"
        >
          Learn React
        </a>

        <DataTable
          value={messages}
          expandedRows={expandedRows}
          onRowToggle={(e) => setExpandedRows(e.data)}
          dataKey="id"
          rowExpansionTemplate={rowExpansionTemplate}
        >
          <Column expander={true} />
          <Column field="From" header="Sender" sortable />
          <Column header="Message" body={openMessageTemplate} />
          <Column field="averageDist" header="Avg Dist" sortable />
          <Column field="numNeighbors" header="# Neighbors" sortable />
        </DataTable>

      </header>
    </div>
  );
}

export default App;
