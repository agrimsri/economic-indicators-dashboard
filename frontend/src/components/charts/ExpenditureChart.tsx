import React, { useMemo } from 'react'
import ReactECharts from 'echarts-for-react'
import * as echarts from 'echarts'
import type { SeriesData } from '../../types/dashboard'
import { axisStyle, commonChartTheme } from './chartUtils'

interface ExpenditureChartProps {
  series: SeriesData[]
}

export const ExpenditureChart: React.FC<ExpenditureChartProps> = ({ series }) => {
  const option = useMemo(() => {
    const capSeries = series.find(
      (s) => s.key === 'capital_expenditure' || s.label.toLowerCase().includes('capital')
    )
    const revSeries = series.find(
      (s) => s.key === 'revenue_expenditure' || s.label.toLowerCase().includes('revenue')
    )
    const totSeries = series.find(
      (s) => s.key === 'total_expenditure' || s.label.toLowerCase().includes('total')
    )

    const categories = Array.from(
      new Set([
        ...(capSeries?.points.map((p) => p.x) || []),
        ...(revSeries?.points.map((p) => p.x) || []),
      ])
    ).sort()

    const capData = categories.map((cat) => {
      const pt = capSeries?.points.find((p) => p.x === cat)
      return pt?.y ?? 0
    })

    const revData = categories.map((cat) => {
      const pt = revSeries?.points.find((p) => p.x === cat)
      return pt?.y ?? 0
    })

    const totData = categories.map((cat, idx) => {
      const explicitTot = totSeries?.points.find((p) => p.x === cat)?.y
      if (explicitTot !== undefined && explicitTot !== null) return explicitTot
      return roundTwo(capData[idx] + revData[idx])
    })

    function roundTwo(num: number) {
      return Math.round((num + Number.EPSILON) * 100) / 100
    }

    return {
      ...commonChartTheme,
      legend: {
        ...commonChartTheme.legend,
        data: ['Capital Expenditure', 'Revenue Expenditure'],
      },
      xAxis: {
        type: 'category',
        data: categories,
        ...axisStyle,
      },
      yAxis: {
        type: 'value',
        name: '₹ Lakh Cr',
        nameTextStyle: { color: '#94a3b8', fontSize: 11 },
        ...axisStyle,
        axisLabel: {
          ...axisStyle.axisLabel,
          formatter: '₹{value}',
        },
      },
      series: [
        {
          name: 'Capital Expenditure',
          type: 'bar',
          stack: 'total',
          data: capData,
          barMaxWidth: 26,
          itemStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: '#ffa73f' },
              { offset: 1, color: '#964800' },
            ]),
          },
        },
        {
          name: 'Revenue Expenditure',
          type: 'bar',
          stack: 'total',
          data: revData,
          barMaxWidth: 26,
          itemStyle: {
            borderRadius: [4, 4, 0, 0],
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: '#0fb8e6' },
              { offset: 1, color: '#004c7d' },
            ]),
          },
          label: {
            show: true,
            position: 'top',
            color: '#ffffff',
            fontSize: 11,
            fontWeight: 600,
            formatter: (params: { dataIndex: number }) => {
              const total = totData[params.dataIndex]
              return total ? `₹${total}` : ''
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
