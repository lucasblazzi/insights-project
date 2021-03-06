import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import './styles.css';
import logo from '../Login/Insights_branco.png';

const NavBar = () => {
  const navigate = useNavigate();

  function onClick(event) {
    event.preventDefault();

    navigate('/login');
  }

  return (
    <nav className="nav-navbar">
      <h1 className="title">
        <img src={logo} alt="logo" width="70" />
      </h1>
      <ul>
        <li>
          <NavLink
            activeClassName="active-nav-name"
            className="nav-name"
            to="/"
            end
          >
            Registrar Interesses
          </NavLink>
        </li>
        <li>
          <NavLink
            activeClassName="active-nav-name"
            className="nav-name"
            to="tips"
          >
            Acompanhar Dicas
          </NavLink>
        </li>
        <li>
          <NavLink
            activeClassName="active-nav-name"
            className="nav-name"
            to="kpi"
          >
            KPI
          </NavLink>
        </li>
        <li>
          <span className="nav-name" onClick={onClick}>
            Sair
          </span>
        </li>
      </ul>
    </nav>
  );
};

export default NavBar;
