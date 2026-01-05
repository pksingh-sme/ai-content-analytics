import React from 'react';
import { Link, NavLink } from 'react-router-dom';
import styled from 'styled-components';

const HeaderContainer = styled.header`
  background-color: #2c3e50;
  padding: 1rem 2rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
`;

const Nav = styled.nav`
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const Logo = styled(Link)`
  color: white;
  font-size: 1.5rem;
  font-weight: bold;
  text-decoration: none;
`;

const NavLinks = styled.div`
  display: flex;
  gap: 1.5rem;
`;

const StyledNavLink = styled(NavLink)`
  color: #ecf0f1;
  text-decoration: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  transition: background-color 0.2s;

  &:hover {
    background-color: #34495e;
  }

  &.active, &.active:hover {
    background-color: #3498db;
  }
`;

const Header: React.FC = () => {
  return (
    <HeaderContainer>
      <Nav>
        <Logo to="/">Multi-Modal Content Analytics</Logo>
        <NavLinks>
          <StyledNavLink to="/">Dashboard</StyledNavLink>
          <StyledNavLink to="/upload">Upload</StyledNavLink>
          <StyledNavLink to="/search">Search</StyledNavLink>
          <StyledNavLink to="/chat">Chat</StyledNavLink>
        </NavLinks>
      </Nav>
    </HeaderContainer>
  );
};

export default Header;