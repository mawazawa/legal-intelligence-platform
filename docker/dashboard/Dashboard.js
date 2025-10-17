import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
  Container,
  Grid,
  Paper,
  Typography,
  Box,
  Card,
  CardContent,
  LinearProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Button,
  TextField,
  Tab,
  Tabs
} from '@mui/material';
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';
import { styled } from '@mui/material/styles';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || '/api';

const StyledPaper = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(3),
  margin: theme.spacing(2),
  backgroundColor: '#f5f5f5',
  borderRadius: 12,
  boxShadow: '0 4px 20px rgba(0,0,0,0.1)'
}));

const MetricCard = ({ title, value, unit, color }) => (
  <Card sx={{ height: '100%', bgcolor: color, color: 'white' }}>
    <CardContent>
      <Typography variant="h6" gutterBottom>{title}</Typography>
      <Typography variant="h3">{value}</Typography>
      <Typography variant="body2">{unit}</Typography>
    </CardContent>
  </Card>
);