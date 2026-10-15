import React, { useMemo } from 'react'
import ReactECharts from 'echarts-for-react'
import * as echarts from 'echarts'
import type { SeriesData } from '../../types/dashboard'
import { axisStyle, commonChartTheme } from './chartUtils'

interface DebtChartProps {
  series: SeriesData[]
}

export const DebtChart: React.FC<DebtChartProps> = ({ series }) => {
  const option = useMemo(() => {
    const mainSeries = series[0]
    const points = mainSeries?.points || []

    const xData = points.map((p) => p.x)
    const yData = points.map((p) => p.y)

    return {
      ...commonChartTheme,
      legend: {
        ...commonChartTheme.legend,
        data: ['Debt to GDP'],
      },
      xAxis: {
        type: 'category',
        data: xData,
        ...axisStyle,
      },
      yAxis: {
        type: 'value',
        ...axisStyle,
        axisLabel: {
          ...axisStyle.axisLabel,
          formatter: '{value}%',
        },
      },
      series: [
        {
          name: 'Debt to GDP',
          type: 'line',
          smooth: true,
          data: yData,
          showSymbol: true,
          symbolSize: 8,
          itemStyle: {
            color: '#0fb8e6',
          },
          lineStyle: {
            width: 3,
            color: '#0fb8e6',
            shadowColor: 'rgba(15, 184, 230, 0.4)',
            shadowBlur: 10,
          },
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: 'rgba(15, 184, 230, 0.35)' },
              { offset: 1, color: 'rgba(15, 184, 230, 0.02)' },
            ]),
          },
          markPoint: {
            data: [
              { type: 'max', name: 'Max' },
              { type: 'min', name: 'Min' },
            ],
            itemStyle: {
              color: '#0fcaf0',
            },
            label: {
              color: '#07122a',
              fontWeight: 700,
              fontSize: 10,
              formatter: '{c}%',
            },
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
