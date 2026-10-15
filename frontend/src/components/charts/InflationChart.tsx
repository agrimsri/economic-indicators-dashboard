import React, { useMemo } from 'react'
import ReactECharts from 'echarts-for-react'
import type { SeriesData } from '../../types/dashboard'
import { axisStyle, commonChartTheme } from './chartUtils'

interface InflationChartProps {
  series: SeriesData[]
}

export const InflationChart: React.FC<InflationChartProps> = ({ series }) => {
  const option = useMemo(() => {
    const cpiSeries = series.find(
      (s) => s.key === 'cpi' || s.label.toLowerCase().includes('cpi')
    )

    const categories = (cpiSeries?.points || []).map((p) => p.x)
    const cpiData = (cpiSeries?.points || []).map((p) => p.y)

    return {
      ...commonChartTheme,
      legend: {
        ...commonChartTheme.legend,
        data: ['CPI YoY (%)', 'RBI Target (4%)'],
      },
      xAxis: {
        type: 'category',
        data: categories,
        ...axisStyle,
      },
      yAxis: {
        type: 'value',
        ...axisStyle,
        min: 0,
        max: 8,
        axisLabel: {
          ...axisStyle.axisLabel,
          formatter: '{value}%',
        },
      },
      series: [
        {
          name: 'CPI YoY (%)',
          type: 'line',
          smooth: true,
          data: cpiData,
          showSymbol: true,
          symbolSize: 8,
          itemStyle: {
            color: '#0fb8e6',
          },
          lineStyle: {
            width: 3,
            color: '#0fb8e6',
          },
          markLine: {
            symbol: 'none',
            data: [
              {
                yAxis: 4.0,
                name: 'RBI Target (4%)',
                lineStyle: {
                  color: '#f4e15c',
                  type: 'dashed',
                  width: 2,
                },
                label: {
                  show: true,
                  position: 'insideEndTop',
                  formatter: 'RBI Target: 4.0%',
                  color: '#f4e15c',
                  fontSize: 11,
                },
              },
            ],
          },
          markArea: {
            silent: true,
            itemStyle: {
              color: 'rgba(244, 225, 92, 0.08)',
            },
            data: [
              [
                {
                  yAxis: 2.0,
                  name: 'Tolerance Band (2-6%)',
                },
                {
                  yAxis: 6.0,
                },
              ],
            ],
          },
        },
        {
          name: 'RBI Target (4%)',
          type: 'line',
          data: [],
          itemStyle: {
            color: '#f4e15c',
          },
          lineStyle: {
            color: '#f4e15c',
            type: 'dashed',
            width: 2,
          },
        },
      ],
    }
  }, [series])

  return (
    <div style={{ width: '100%', height: '100%', minHeight: '290px' }}>
      <ReactECharts
        option={option}
        style={{ width: '100%', height: '100%', minHeight: '290px' }}
        opts={{ renderer: 'canvas' }}
        notMerge={true}
      />
    </div>
  )
}
