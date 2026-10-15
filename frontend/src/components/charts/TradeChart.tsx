import React, { useMemo } from 'react'
import ReactECharts from 'echarts-for-react'
import * as echarts from 'echarts'
import type { SeriesData } from '../../types/dashboard'
import { axisStyle, commonChartTheme } from './chartUtils'

interface TradeChartProps {
  series: SeriesData[]
}

export const TradeChart: React.FC<TradeChartProps> = ({ series }) => {
  const option = useMemo(() => {
    const expSeries = series.find(
      (s) => s.key === 'exports' || s.label.toLowerCase().includes('export')
    )
    const impSeries = series.find(
      (s) => s.key === 'imports' || s.label.toLowerCase().includes('import')
    )
    const balSeries = series.find(
      (s) => s.key === 'trade_balance' || s.label.toLowerCase().includes('balance')
    )

    const categories = Array.from(
      new Set([
        ...(expSeries?.points.map((p) => p.x) || []),
        ...(impSeries?.points.map((p) => p.x) || []),
      ])
    ).sort()

    const expData = categories.map((cat) => {
      const pt = expSeries?.points.find((p) => p.x === cat)
      return pt?.y ?? null
    })

    const impData = categories.map((cat) => {
      const pt = impSeries?.points.find((p) => p.x === cat)
      return pt?.y ?? null
    })

    const balData = categories.map((cat) => {
      const pt = balSeries?.points.find((p) => p.x === cat)
      return pt?.y ?? null
    })

    return {
      ...commonChartTheme,
      legend: {
        ...commonChartTheme.legend,
        data: ['Imports', 'Exports', 'Trade Balance'],
      },
      xAxis: {
        type: 'category',
        data: categories,
        ...axisStyle,
      },
      yAxis: {
        type: 'value',
        name: 'US$ B',
        nameTextStyle: {
          color: '#94a3b8',
          fontSize: 11,
        },
        ...axisStyle,
        axisLabel: {
          ...axisStyle.axisLabel,
          formatter: '${value}B',
        },
      },
      series: [
        {
          name: 'Imports',
          type: 'bar',
          data: impData,
          barMaxWidth: 20,
          itemStyle: {
            borderRadius: [4, 4, 0, 0],
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: '#0fb8e6' },
              { offset: 1, color: '#005282' },
            ]),
          },
        },
        {
          name: 'Exports',
          type: 'bar',
          data: expData,
          barMaxWidth: 20,
          itemStyle: {
            borderRadius: [4, 4, 0, 0],
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: '#ffa73f' },
              { offset: 1, color: '#8c4400' },
            ]),
          },
        },
        {
          name: 'Trade Balance',
          type: 'line',
          data: balData,
          showSymbol: true,
          symbolSize: 7,
          itemStyle: {
            color: '#69f6b8',
          },
          lineStyle: {
            width: 2.5,
            color: '#69f6b8',
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
